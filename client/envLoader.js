const path = require('path')


module.exports = function (source) {
  const envVars = [...source.matchAll(/process\.env\.\w+/g)]
  envVars.sort((a, b) => b[0].length - a[0].length)
  envVars.forEach((envVar) => {
    envVar = envVar[0].split('.').pop()
    replace = process.env[envVar] ? `'${process.env[envVar]}'` : 'null'
    let regex = new RegExp(`process\.env\.${envVar}`, 'g')
    source = source.replaceAll(regex, replace)
  })

  return source
}
