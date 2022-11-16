import {v4 as uuid} from 'uuid';
import RejectConflictRequestScheduler from './reject_conflict_request_scheduler';
import QueueRequestScheduler from './queue_request_scheduler';
import iframeClientUtil from './iframe_client_util';
import config from '../config'


const RequestSchedulerFactory = {
  rejectConflict: RejectConflictRequestScheduler,
  queue: QueueRequestScheduler,
};


/**
 * A Client which allows embedded Iframe apps to communicate with the parent Dialpad via postMessages.
 *
 * To initialize the Dialpad Client create an instance of the client and call client.init():
 *    var client = DialpadClient();
 *    client.init().then((initData) => {});
 *
 * Once the promise returned by the call to client.init() resolves, data can be requested from the client.
 *    client.getCurrentUser().then((userData) => {})
 *    client.getCurrentContact().then((contactData) => {})
 */
class DialpadClient {
  constructor (conf = {}) {
    console.log('=========CONFIG', config)
    this.dialpadUri = conf.dialpadUri || config.DIALPAD_URL;
    console.log('=========dialpaduri', this.dialpadUri)
    this.clientUid = window.name;
    this.window = window.parent;
    this.isInitialized = false;
    this.requestScheduler = this._createRequestScheduler(conf);
    this._addListener();
  }

  _addListener () {
    console.log('===ADDING LISTENER');
    this.listenerCallback = (request) => {
      console.log('===CALLBACK', request.data);
      const data = request.data;
      console.log('===TYPE', data.type);
      if (data.type === 'webpackOk') return
      console.log('===START SANITIZE');
      if (!this._sanitize(request)) return;
      console.log('===PASSS SANITIZE');
      this.requestScheduler.executeHandler(data);
    };

    window.addEventListener('message', this.listenerCallback);
  }

  /**
   * Returns Promise for Dialpad Client initializing request.
   * Sends initial postMessage to Dialpad app and adds handler
   * for replying initialization postMessage.
   */
  init () {
    return this.requestScheduler.initiateInitRequest();

  }

  /**
   * Returns Promise resolving with data for the current Dialpad user.
   * Sends postMessage requesting user data from Dialpad app and adds
   * handler for replying postMessage.
   */
  getCurrentUser () {
    return this.requestScheduler.initiateGetRequest('get/user');
  }

  /**
   * Returns Promise resolving with data for the active Dialpad contact.
   * Sends postMessage requesting contact data from Dialpad app and adds
   * handler for replying postMessage.
   */
  getCurrentContact () {
    return this.requestScheduler.initiateGetRequest('get/contact');
  }

  /**
   * Returns Promise resolving with data for the active Dialpad call.
   * Sends postMessage requesting call data from Dialpad app and adds
   * handler for replying postMessage.
   */
  getCurrentCall () {
    return this.requestScheduler.initiateGetRequest('get/call');
  }

  /**
   * Subscribes to call events, invoking the callback on each event.
   * Sends postMessage requesting initiating subscription with Dialpad
   * app and adds handler for replying postMessages.
   * @param {Function} callback : The callback to be invoked for each event.
   */
  onCallState (callback) {
    return this.requestScheduler.initiateOnRequest('on/call', callback);
  }

  /**
   * Removes subscription to call events created with callback.
   * @param {Function} callback : The callback used in initial subscription.
   */
  offCallState (callback) {
    return this.requestScheduler.initiateOffRequest('off/call', callback);
  }

  /**
   * Subscribes to disconnect event, invoking the callback on each event.
   * Sends postMessage requesting initiating subscription with Dialpad
   * app and adds handler for replying postMessages.
   * @param {Function} callback : The callback to be invoked for each event.
   */
  onDisconnect (callback) {
    return this.requestScheduler.initiateOnRequest('on/disconnect', callback);
  }

  /**
   * Removes subscription to disconnect event created with callback.
   * @param {Function} callback : The callback used in initial subscription.
   */
  offDisconnect (callback) {
    return this.requestScheduler.initiateOffRequest('off/disconnect', callback);
  }

  auth (callback, content) {
    const messageUid = uuid();
    return this.requestScheduler.initiateRequest('auth/external', callback, messageUid, content,
      120000);
  }

  /**
   * Send a toast message which will be consumed by dialpad, with callback
   * @param callback: The callback to be invoked for each toast
   * @param content: The data that should be passed to dialpad
   * @returns {Promise<any> | Promise}
   */
  sendToast (callback, content) {
    const messageUid = uuid();
    return this.requestScheduler.initiateRequest('send/toast', callback, messageUid, content);
  }

  /**
   * Send mapped object data which will be consumed by dialpad, with callback
   * @param callback: the callback to be invoked, once the request complete
   * @param content: The data that should be passed to dialpad
   * @returns {Promise<any> | Promise}
   */
  setContactDetails (callback, content) {
    const messageUid = uuid();
    return this.requestScheduler.initiateRequest('set/contact', callback, messageUid, content);
  }

  trackEvent (callback, content) {
    const messageUid = uuid();
    return this.requestScheduler.initiateRequest('track/event', callback, messageUid, content);
  }

  shouldPopCrmPage (callback) {
    return this.requestScheduler.initiateRequest('get/screen_pop', callback);
  }

  _createRequestScheduler (config) {
    const SchedulerClass = RequestSchedulerFactory[config.schedulerType] || RequestSchedulerFactory.rejectConflict;
    return new SchedulerClass(this.dialpadUri);
  }

  _sanitize (request) {
    // Check the origin of this request is in allowed origins for client.
    console.log('===SANITIZE');
    if (!this._checkAllowedUrl(request.origin)) {
      console.log('===NOTALLOWED', request.origin);
      const errorMessage = `Event origin: ${request.origin} is invalid.`;
      iframeClientUtil.logErrorMessage(errorMessage, request.data);
      return false;
    }

    const data = request.data;
    const clientUid = data.client_uid;

    // Check request data has required fields.
    if (!this._hasRequiredFields(data)) {
      const errorMessage = `One of client_uid: ${data.client_uid} or message_uid ${data.message_uid} is missing from request data.`;
      iframeClientUtil.logErrorMessage(errorMessage, request.data);
      return false;
    }

    // Check request clientUid matches that of this client.
    if (!this.clientUid === clientUid) {
      const errorMessage = `ClientUid: ${this.clientUid} does not match ClientUid: ${clientUid}`;
      iframeClientUtil.throwClientError(errorMessage, request.data);
    }

    return true;
  }

  _hasRequiredFields (data) {
    return data.service && data.client_uid && data.context && data.path;
  }

  _isAllowedOrigin (requestOrigin, allowedOrigin) {
    if (!allowedOrigin.includes('*')) {
      return requestOrigin === allowedOrigin;
    }
    const requestUrl = new URL(requestOrigin);
    const allowedUrl = new URL(allowedOrigin.replace('*', ''));
    return requestUrl.protocol === allowedUrl.protocol && requestUrl.hostname.endsWith(allowedUrl.hostname);
  }

  _checkAllowedUrl (requestOrigin) {
    console.log('===ALLOWED', config.DIALPAD_CLIENT_ALLOWED_ORIGINS);
    console.log('===requestOrigin', requestOrigin);
    return config.DIALPAD_CLIENT_ALLOWED_ORIGINS.some(allowedOrigin => {
      console.log('===ALLOWED ORIGIN', allowedOrigin)
      console.log('===REQUEST ORIGIN', requestOrigin)
      return this._isAllowedOrigin(requestOrigin, allowedOrigin);
    });
  }

}

export default DialpadClient;
