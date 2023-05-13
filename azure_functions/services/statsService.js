const mongoose = require('mongoose');
const db = require('../db/mongodb');
const statsSchema = require('../db/stats').statsSchema
const Stats = mongoose.model("Stats", statsSchema);

const getStats = async (context) => {
    db.connectToDatabase();

    await Stats.find().then((stats) => {
        context.res = {
            status: 200,
            body: stats,
            headers: { "Access-Control-Allow-Origin": "*" }
        };
    }).catch((error) => {
        context.res = {
            status: 400,
            body: "Error getting stats",
            headers: { "Access-Control-Allow-Origin": "*" }
        };
    });
}

module.exports = {
    getStats
}