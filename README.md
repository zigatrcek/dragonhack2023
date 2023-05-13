# DragonHack2023 submission: a smart trashcan

Hi, we are team Takle mamo, you can see our DragonHack application 
<a href="https://github.com/anablaz/Dragonhack_2023_application" target="_blank">here</a>.

For Dragonhack 2023, we built a smart trashcan utilising embedded computer vision and neural networks. The motivation behind our project was the fact that over 25% of trash in Slovenia 
<a href="https://www.stat.si/StatWeb/Field/Index/13/70" target="_blank">still doesn't get recycled correctly</a>. Our project is a team effort to reduce this number.

When the user approaches with a piece of trash, the DepthAI camera on the trashcan detects the item and determines in which recycling category it belongs (packaging, paper, and "other", similar as to most trashcans in Slovenia). The LED lights on the trashcan, powered by an embedded software ran on ESP32 (Arduino), light up around the relevant recycling box. That way, the user can understand with ease how to dispose of their item correctly.

To further inform our users, we built a counter of items discarded into each one of the recycling boxes, using Azure Functions and MongoDB.

The product can be scaled in many additional ways, the main one being upgraded with an automated recycling system, where the individual items of trash get sorted by the trashcan itself. It also holds a lot of potential for being used in the educational institutions. Its another advantage is that it can be built significantly cheaper compared to the other products on the market. Because of its educational and environmental impact, we believe it could also qualify for the  European Regional Development Fund in the future.
