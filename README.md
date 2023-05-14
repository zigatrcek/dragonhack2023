# DragonHack2023 submission: a smart trash can

## Team Information

Hi, we are team Takle mamo, you can see our DragonHack application and team information
<a href="https://github.com/anablaz/Dragonhack_2023_application" target="_blank">here</a>.

## Project Motivation

For Dragonhack 2023, we built a smart trash can that utilises embedded computer vision and neural networks to help users make smarter recycling decisions. The motivation behind our project was the fact that over 25% of trash in Slovenia
<a href="https://www.stat.si/StatWeb/Field/Index/13/70" target="_blank">still doesn't get recycled correctly</a>. Our project is a team effort to reduce this number.

## Functionality

When the user approaches with a piece of trash, the DepthAI camera on the trash can detects the item and determines which recycling category it belongs into (packaging, paper, and "other", similar to most public trash cans in Slovenia). The entire detection and classification process runs on the embedded device itself and doesn't rely on a host computer. The LED lights on the trashcan, powered by an embedded software ran on ESP32 (Arduino), light up around the relevant recycling box. That way, the user can easily understand how to dispose of their item correctly.

![Working example](src/img/demo.gif)

To further inform our users, we built a counter of items discarded into each one of the recycling boxes, using a serverless architecture (Azure Functions) and MongoDB.

## Market opportunity

The product is mainly designed to be used in public spaces, such as schools, universities, and offices. It's suitable for these situations, as users who use recycling cans there usually only bring single items as opposed to large bags of garbage that are difficult to classify. We believe it is an ideal tool for helping children learn which items to recycle and where. The environmental and educational impact makes the idea a strong candidate to receive funding from the European Regional Development Fund.

The product could naturally also be used in private households, however, it could prove to be too expensive for the average household.

## Upsides

This smart recycling can be built significantly cheaper compared to other similar products on the market. It is very versatile as a LED strip can be placed around any existing trash can with very little adaptation, making it a very cost-effective solution.
## Possible improvements

The product can be upgraded in many additional ways. It could be equipped with an automated garbage sorting system that classifies items as they get inserted into it, sorting them automatically afterwards.

Similarly, it could sense the items passing into the box and provide a unique user experience by giving auditory feedback to the user. This could be done by playing a sound that notifies the user if they discarded the item correctly or not.
