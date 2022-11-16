function logErrorMessage (message, data) {
  console.warn(_buildBaseMessage(data));
  console.warn(message);
}

function _buildBaseMessage (data) {
  return `DIALPAD CLIENT: ClientUid: ${data.client_uid}, MessageUid: ${data.message_uid}, Service: ${data.service}, Context: ${data.context}, Path: ${data.path}`;
}

function throwClientError (message, data) {
  console.warn(_buildBaseMessage(data));
  throwError(message);
}

function throwError (message) {
  console.warn(message);
  throw new Error(message);
}

function convertToSubscriberPath (unSubscriberPath) {
  const pathBase = unSubscriberPath.split('/')[1];
  return `on/${pathBase}`;
}

export default { logErrorMessage, throwClientError, throwError, convertToSubscriberPath };
