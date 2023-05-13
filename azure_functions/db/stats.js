const mongoose = require("mongoose")

const statsSchema = new mongoose.Schema(
    {
        container: Number,
        paper: Number,
        other: Number
    },
    { timestamps: true });

mongoose.model("Stats", statsSchema, "Stats");

module.exports = {
    statsSchema
}