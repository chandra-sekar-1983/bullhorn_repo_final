import BaseRequestScheduler from './base_request_scheduler';
import iframeClientUtil from './iframe_client_util';
import iframeConstants from './iframe_constants';

/**
 * The default implementation of the request scheduler. If multiple messages are in flight
 * for a given path the DialpadClient will reject with an error.
 */

class RejectConflictRequestScheduler extends BaseRequestScheduler {
  constructor (dialpadUri) {
    super(dialpadUri);
    this.inFlightPaths = new Set();
  }

  /**
   * Returns Promise of data returned by DialpadClient request. Initiates
   * request to Dialpad app.
   * @param {String} path : The path of the request (e.g. 'get/user').
   * @param {Function} handler : The callback to be called on returned data.
   */
  initiateRequest (path, handler) {
    return new Promise((resolve, reject) => {
      if (this.inFlightPaths.has(path)) {
        const message = `Error: Request to path: ${path} is already in progress.`;
        console.warn(message);
        return reject(new Error(message));
      }
      this.inFlightPaths.add(path);
      BaseRequestScheduler.prototype.initiateRequest.call(this, path, handler)
        .then(resolve)
        .catch(reject)
        .finally(() => {
          this.inFlightPaths.delete(path);
        });
    });
  }

  /**
   * Performs common actions for adding subscription postMessage responses.
   * @param {Object} data : Data object returned by postMessage.
   * @param {Function} callback : The callback to be called on returned data.
   */
  _onOnHandleResponse (data, callback) {
    if (data.status_code === iframeConstants.OK) {
      callback(data.content);
    }
  }

  /**
   * Handles error responses from Dialpad.
   * @param {Object} data : Data object returned by postMessage.
   */
  handleErrorResponse (data) {
    this.inFlightPaths.delete(data.path);
    BaseRequestScheduler.prototype.handleErrorResponse.call(this, data);
  }

  /**
   * Common response handling logic.
   * @param {Object} data : Data object returned by postMessage.
   */
  _onGetHandleResponse (data) {
    BaseRequestScheduler.prototype._onGetHandleResponse.call(this, data);
    this.inFlightPaths.delete(data.path);
  }

  /**
   * Performs common actions for removing subscription postMessage responses.
   * @param {Object} data : Data object returned by postMessage.
   */
  _onOffHandleResponse (data) {
    BaseRequestScheduler.prototype._onOffHandleResponse.call(this, data);
    this.inFlightPaths.delete(data.path);
    const subscriberPath = iframeClientUtil.convertToSubscriberPath(data.path);
    this.inFlightPaths.delete(subscriberPath);
  }
}

export default RejectConflictRequestScheduler;
