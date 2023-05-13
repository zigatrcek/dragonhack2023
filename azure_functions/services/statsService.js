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

const addStats = async (context, stats) => {
    db.connectToDatabase();

    const newStats = new Stats(stats);
    await newStats.save().then((stats) => {
        context.res = {
            status: 201,
            body: stats
        };
    }).catch((err) => {
        context.res = {
            status: 400,
            body: "Error adding stats." + err
        };
    });
}

module.exports = {
    getStats,
    addStats
}