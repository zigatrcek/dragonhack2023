const statsService = require('../services/statsService')

module.exports = async function (context, req) {
    context.log('JavaScript HTTP trigger function processed a request.');

    if (req.method == "GET") {
        await statsService.getStats(context)
    }
}