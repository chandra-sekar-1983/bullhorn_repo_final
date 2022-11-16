
/**
 * A convenience class for tracking callbacks for an 'on' request
 * from the DialpadClient. Tracking of callbacks in this manner allows
 * removal of a specific callback using an 'off' request.
 *
 * Two callbacks are compared via their reference NOT their string value.
 */
class CallbackRegistry {
  constructor () {
    this._registry = {};
  }

  /**
   * Returns subscribed <messageUid>: <callback> pairs for a given path.
   * @param {String} path : The path for the subscribed callback
   */
  getRegisteredForPath (path) {
    return this._registry[path] || {};
  }

  /**
   * Adds a <messageUid>: <callback> pair to the registry for a given path.
   * @param {String} path : The path for the subscribed callback
   * @param {Function} callback : Function to be called by subscribed to 'on' events.
   * @param {String} messageUid : The messageUid of the 'on' request that created the subscription.
   */
  addCallbackToRegistry (path, callback, messageUid) {
    if (this.getMessageUid(path, callback)) {
      throw Error(`Callback is already registered for path: ${path}`);
    }
    const registeredCallbacks = this.getRegisteredForPath(path);
    registeredCallbacks[messageUid] = callback;
    this._registry[path] = registeredCallbacks;
  }

  /**
   * Removes a <messageUid>: <callback> pair from the registry for a given path.
   * @param {String} path : The path for the subscribed callback
   * @param {String} messageUid : The messageUid of the 'on' request that created the subscription.
   */
  removeFromRegistry (path, messageUid) {
    let registeredCallbacks = this._getEntriesForPath(path);
    registeredCallbacks = registeredCallbacks.filter((mapping) => {
      return messageUid !== mapping[0];
    });
    this._registry[path] = registeredCallbacks;
  }

  /**
   * Retrieves a the messageUid paired with a callback for a given path.
   * @param {String} path : The path for the subscribed callback
   * @param {Function} callback : Function to be called by subscribed to 'on' events.
   */
  getMessageUid (path, callback) {
    const registeredCallbacks = this._getEntriesForPath(path);
    const callbackMapping = registeredCallbacks.find(([messageUid, registeredCallback]) => {
      return callback == registeredCallback; // eslint-disable-line eqeqeq
    }) || [];
    return callbackMapping[0];
  }

  _getEntriesForPath (path) {
    return Object.entries(this.getRegisteredForPath(path));
  }
}

export default CallbackRegistry;
