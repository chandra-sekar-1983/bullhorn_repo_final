import BaseRequestScheduler from './base_request_scheduler';
import iframeConstants from './iframe_constants';

/**
 * Implementation of the request scheduler using a single queue. Requests (postMessages) are
 * sent one at a time. If a request is in flight new requests are instead added to the queue.
 * once a response is received the next request is sent.
 */

class QueueRequestScheduler extends BaseRequestScheduler {
  constructor (dialpadUri) {
    super(dialpadUri);
    this.messageQueue = new Map();
  }

  /**
   * Common response handling logic.
   * @param {Object} data: Data object returned by postMessage.
   */
  _onGetHandleResponse (data) {
    BaseRequestScheduler.prototype._onGetHandleResponse.call(this, data);
    this._queueNextRequest(data.message_uid);
  }

  /**
   * Performs common actions for adding subscription postMessage responses.
   * @param {Object} data : Data object returned by postMessage.
   * @param {Function} callback : The callback to be called on returned data.
   */
  _onOnHandleResponse (data, callback) {
    if (data.status_code === iframeConstants.SUBSCRIPTION_ADDED) {
      this._queueNextRequest(data.message_uid);
      return;
    }
    callback(data.content);
  }

  /**
   * Handles error responses from Dialpad.
   * @param {Object} data : Data object returned by postMessage.
   */
  handleErrorResponse (data) {
    this._queueNextRequest(data.message_uid);
    BaseRequestScheduler.prototype.handleErrorResponse.call(this, data);
  }

  /**
   * Executes handler for respective data object.
   * @param {Object} data : Data object returned by postMessage.
   */
  executeHandler (data) {
    BaseRequestScheduler.prototype.executeHandler.call(this, data);
    this._queueNextRequest(data.message_uid);
  }

  _sendRequest (path, messageUid, content) {
    const isNextInQueue = !!this._nextRequestInQueue();
    this._addRequestToQueue(messageUid, path, content);

    // If no previous request in the queue, send the new request.
    if (!isNextInQueue) {
      const currentRequest = this._nextRequestInQueue();
      currentRequest();
    }
  }

  _onTimeout (messageUid, reject) {
    if (!this.messageQueue.get(messageUid)) return;
    BaseRequestScheduler.prototype._onTimeout.call(this, messageUid, reject);
  }

  _addRequestToQueue (messageUid, path, content) {
    this.messageQueue.set(messageUid, () => {
      this._sendData(path, messageUid, content);
    });
  }

  _queueNextRequest (messageUid) {
    this.messageQueue.delete(messageUid);
    const nextRequest = this._nextRequestInQueue();

    if (nextRequest) {
      nextRequest();
    }
  }

  _nextRequestInQueue () {
    return this.messageQueue.values().next().value;
  }
}

export default QueueRequestScheduler;
