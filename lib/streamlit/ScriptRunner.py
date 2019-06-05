# Copyright 2019 Streamlit Inc. All rights reserved.
# -*- coding: utf-8 -*-

import sys
import threading
from collections import deque

from blinker import Signal

from streamlit import config
from streamlit import magic
from streamlit.watcher.LocalSourcesWatcher import LocalSourcesWatcher

from streamlit.logger import get_logger
LOGGER = get_logger(__name__)


class ScriptState(object):
    RUNNING = 'RUNNING'
    STOPPED = 'STOPPED'
    IS_SHUTDOWN = 'IS_SHUTDOWN'


class ScriptEvent(object):
    # Stop the script, but don't shutdown the runner (no data)
    STOP = 'STOP'
    # Rerun the script (data=Report)
    RERUN = 'RERUN'
    # Shut down the ScriptRunner, stopping any running script first (data=None)
    SHUTDOWN = 'SHUTDOWN'


class ScriptEventQueue(object):
    """A thread-safe queue of script-related events.

    ScriptRunner publishes to this queue, and its run thread consumes from it.
    """
    def __init__(self):
        self._cond = threading.Condition()
        # deque, instead of list, because we push to the front and
        # pop from the back
        self._queue = deque()

    def enqueue(self, event, data=None):
        """Enqueue a new event to the end of the queue.

        This event may be coalesced with an existing event if appropriate.
        For example, multiple consecutive RERUN requests will be combined
        so that there's only ever one pending RERUN request in the queue
        at a time.

        Parameters
        ----------
        event : ScriptEvent
            The type of event

        data : Any
            Data associated with the event, if any
        """
        with self._cond:
            if event == ScriptEvent.SHUTDOWN:
                # If we get a shutdown request, it goes to the front of the
                # queue to be processed immediately.
                self._queue.append((event, data))
            elif event == ScriptEvent.RERUN:
                index = _index_if(self._queue, lambda item: item[0] == event)
                if index >= 0:
                    # Overwrite existing rerun
                    self._queue[index] = (event, data)
                else:
                    self._queue.appendleft((event, data))
            else:
                self._queue.appendleft((event, data))

            # Let any consumers know that we have new data
            self._cond.notify()

    def dequeue_nowait(self):
        """Pops the front-most event from the queue and returns it.

        If the queue is empty, None will be returned instead.

        Returns
        -------
        A (ScriptEvent, Data) tuple, or (None, None) if the queue is empty.
        """
        return self.dequeue(wait=False)

    def dequeue(self, wait=True):
        """Pops the front-most event from the queue and returns it.

        If the queue is empty, this function will block until there's
        an event to be returned.

        Parameters
        ----------
        wait : bool
            If true, and the queue is empty, the function will block until
            there's an event to be returned. Otherwise, an empty queue
            will result in a return of (None, None)

        Returns
        -------
        A (ScriptEvent, Data) tuple.
        """
        with self._cond:
            while len(self._queue) == 0:
                if not wait:
                    # Early out if the queue is empty and wait=False
                    return None, None
                self._cond.wait()

            return self._queue.pop()


class ScriptRunner(object):
    def __init__(self, report):
        """Initialize.

        Parameters
        ----------
        report : Report
            The report with the script to run.

        """
        self._report = report
        self._event_queue = ScriptEventQueue()
        self._state = ScriptState.STOPPED

        self.run_on_save = config.get_option('server.runOnSave')

        self.on_state_changed = Signal(
            doc="""Emitted when the script's execution state state changes.

            Parameters
            ----------
            state : ScriptState
            """)

        self.on_file_change_not_handled = Signal(
            doc="Emitted when the file is modified and we haven't handled it.")

        self.on_script_compile_error = Signal(
            doc="""Emitted if our script fails to compile.  (*Not* emitted
            for normal exceptions thrown while a script is running.)

            Parameters
            ----------
            exception : Exception
                The exception that was thrown
            """)

        self._local_sources_watcher = LocalSourcesWatcher(
            self._report, self._on_source_file_changed)

        # Will be set to true when we process a SHUTDOWN event
        self._shutdown_requested = False

        # start our thread
        self._run_loop_thread = threading.Thread(
            target=self._loop,
            name='ScriptRunner.loop')
        self._run_loop_thread.start()

    def _set_state(self, new_state):
        if self._state == new_state:
            return

        LOGGER.debug('state: %s -> %s' % (self._state, new_state))
        self._state = new_state
        self.on_state_changed.send(self._state)

    def is_running(self):
        return self._state == ScriptState.RUNNING

    def is_shutdown(self):
        return self._state == ScriptState.IS_SHUTDOWN

    def request_rerun(self):
        """Signal that we're interested in running the script immediately.
        If the script is not already running, it will be started immediately.
        Otherwise, a rerun will be requested.
        """
        if self.is_shutdown():
            LOGGER.warning('Discarding RERUN event after shutdown')
            return
        self._event_queue.enqueue(ScriptEvent.RERUN, self._report)

    def request_stop(self):
        if self.is_shutdown():
            LOGGER.warning('Discarding STOP event after shutdown')
            return
        self._event_queue.enqueue(ScriptEvent.STOP)

    def request_shutdown(self):
        if self.is_shutdown():
            LOGGER.warning('Discarding SHUTDOWN event after shutdown')
            return
        self._event_queue.enqueue(ScriptEvent.SHUTDOWN)

    def maybe_handle_execution_control_request(self):
        if self._run_loop_thread != threading.current_thread():
            # We can only handle execution_control_request if we're on the
            # script execution thread. However, it's possible for deltas to
            # be enqueued (and, therefore, for this function to be called)
            # in separate threads, so we check for that here.
            return

        # Pop the next event from our queue. Don't block if there's no event
        event, event_data = self._event_queue.dequeue_nowait()
        if event is None:
            return

        LOGGER.debug('Received ScriptEvent: %s', event)
        if event == ScriptEvent.STOP:
            raise StopException()
        elif event == ScriptEvent.SHUTDOWN:
            self._shutdown_requested = True
            raise StopException()
        elif event == ScriptEvent.RERUN:
            raise RerunException(event_data)
        else:
            raise RuntimeError('Unrecognized ScriptEvent: %s' % event)

    def _on_source_file_changed(self):
        """One of our source files changed. Schedule a rerun if appropriate."""
        if self.run_on_save:
            self._event_queue.enqueue(ScriptEvent.RERUN, self._report)
        else:
            self.on_file_change_not_handled.send()

    def _loop(self):
        """Our run loop.

        Continually pops events from the event_queue. Ends when we receive
        a SHUTDOWN event.

        """
        while not self._shutdown_requested:
            assert self._state == ScriptState.STOPPED

            # Dequeue our next event. If the event queue is empty, the thread
            # will go to sleep, and awake when there's a new event.
            event, event_data = self._event_queue.dequeue()
            if event == ScriptEvent.STOP:
                LOGGER.debug('Ignoring STOP event while not running')
            elif event == ScriptEvent.SHUTDOWN:
                LOGGER.debug('Shutting down')
                self._shutdown_requested = True
            elif event == ScriptEvent.RERUN:
                self._run_script(event_data)
            else:
                raise RuntimeError('Unrecognized ScriptEvent: %s' % event)

        self._set_state(ScriptState.IS_SHUTDOWN)

    def _install_tracer(self):
        """Install function that runs before each line of the script."""

        def trace_calls(frame, event, arg):
            self.maybe_handle_execution_control_request()
            return trace_calls

        # Python interpreters are not required to implement sys.settrace.
        if hasattr(sys, 'settrace'):
            sys.settrace(trace_calls)

    def _run_script(self, report):
        """Run our script"""
        assert self._state == ScriptState.STOPPED

        # Reset delta generator so it starts from index 0.
        import streamlit as st
        st._reset()

        self._set_state(ScriptState.RUNNING)

        # Compile the script. Any errors thrown here will be surfaced
        # to the user via a modal dialog, and won't result in their
        # previous report disappearing.
        try:
            # Python 3 got rid of the native execfile() command, so we now read
            # the file, compile it, and exec() it. This implementation is
            # compatible with both 2 and 3.
            with open(report.script_path) as f:
                filebody = f.read()

            if config.get_option('runner.magicEnabled'):
                filebody = magic.add_magic(filebody, report.script_path)

            code = compile(
                filebody,
                # Pass in the file path so it can show up in exceptions.
                report.script_path,
                # We're compiling entire blocks of Python, so we need "exec"
                # mode (as opposed to "eval" or "single").
                'exec',
                # Don't inherit any flags or "future" statements.
                flags=0,
                dont_inherit=1,
                # Parameter not supported in Python2:
                # optimize=-1,
            )

        except BaseException as e:
            # We got a compile error. Send the exception onto the client
            # as a SessionEvent and bail immediately.
            LOGGER.debug('Fatal script error: %s' % e)
            self.on_script_compile_error.send(e)
            self._set_state(ScriptState.STOPPED)
            return

        # If we get here, we've successfully compiled our script. The next step
        # is to run it. Errors thrown during execution will be shown to the
        # user as ExceptionElements.

        if config.get_option('runner.installTracer'):
            self._install_tracer()

        rerun_requested_with_data = None

        try:
            # Create fake module. This gives us a name global namespace to
            # execute the code in.
            module = _new_module('__main__')

            # Install the fake module as the __main__ module. This allows
            # the pickle module to work inside the user's code, since it now
            # can know the module where the pickled objects stem from.
            # IMPORTANT: This means we can't use "if __name__ == '__main__'" in
            # our code, as it will point to the wrong module!!!
            sys.modules['__main__'] = module

            # Make it look like command-line args were set to whatever the user
            # asked them to be via the GUI.
            # IMPORTANT: This means we can't count on sys.argv in our code ---
            # but we already knew it from the argv surgery in cli.py.
            # TODO: Remove this feature when we implement interactivity! This is
            # not robust in a multi-user environment.
            sys.argv = report.argv

            # Add special variables to the module's dict.
            module.__dict__['__file__'] = report.script_path

            with modified_sys_path(report):
                exec(code, module.__dict__)

        except RerunException as e:
            rerun_requested_with_data = e.report

        except StopException:
            pass

        except BaseException as e:
            # Show exceptions in the Streamlit report.
            st.exception(e)  # This is OK because we're in the script thread.
            # TODO: Clean up the stack trace, so it doesn't include
            # ScriptRunner.

        finally:
            self._set_state(ScriptState.STOPPED)

        self._local_sources_watcher.update_watched_modules()
        _clean_problem_modules()

        if rerun_requested_with_data is not None:
            self._run_script(rerun_requested_with_data)


class ScriptControlException(BaseException):
    """Base exception for ScriptRunner."""
    pass


class StopException(ScriptControlException):
    """Silently stop the execution of the user's script."""
    pass


class RerunException(ScriptControlException):
    """Silently stop and rerun the user's script."""
    def __init__(self, report):
        self.report = report


def _clean_problem_modules():
    if 'keras' in sys.modules:
        try:
            keras = sys.modules['keras']
            keras.backend.clear_session()
        except:
            pass


def _new_module(name):
    """Create a new module with the given name."""

    if sys.version_info >= (3, 4):
        import types
        return types.ModuleType(name)

    import imp
    return imp.new_module(name)


def _index_if(collection, pred):
    """Find the index of the first item in a collection for which a predicate is true.

    Returns the index, or -1 if no such item exists.
    """
    for index, element in enumerate(collection):
        if pred(element):
            return index
    return -1


# Code modified from IPython (BSD license)
# Source: https://github.com/ipython/ipython/blob/master/IPython/utils/syspathcontext.py#L42
class modified_sys_path(object):
    """A context for prepending a directory to sys.path for a second."""

    def __init__(self, report):
        self._report = report
        self._added_path = False

    def __enter__(self):
        if self._report.script_path not in sys.path:
            sys.path.insert(0, self._report.script_path)
            self._added_path = True

    def __exit__(self, type, value, traceback):
        if self._added_path:
            try:
                sys.path.remove(self._report.script_path)
            except ValueError:
                pass

        # Returning False causes any exceptions to be re-raised.
        return False
