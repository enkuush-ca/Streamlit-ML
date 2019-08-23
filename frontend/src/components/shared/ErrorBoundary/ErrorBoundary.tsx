/**
 * @license
 * Copyright 2018-2019 Streamlit Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React from 'react'
import ErrorElement from '../ErrorElement'
import {logError} from '../../../lib/log'

export interface Props {
  width?: number;
}

export interface State {
  error?: Error|null;
}

/**
 * A component that catches errors that take place when React is asynchronously
 * rendering child components.
 */
class ErrorBoundary extends React.PureComponent<Props, State> {
  public constructor(props: Props) {
    super(props)
    this.state = {
      error: null,
    }
  }

  public static getDerivedStateFromError = (error: Error): State => {
    // Return the state update so the next render will show the fallback UI.
    return {
      error: error,
    }
  }

  public componentDidCatch = (error: Error, info: React.ErrorInfo): void => {
    logError(`${error.name}: ${error.message}\n${error.stack}`)
  }

  public render(): React.ReactNode {
    const {error} = this.state

    if (error) {
      return (
        <ErrorElement width={this.props.width} name={error.name} message={error.message} stack={error.stack}/>
      )
    }
    return this.props.children
  }
}

export default ErrorBoundary
