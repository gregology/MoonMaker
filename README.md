# MoonMaker

### An experiment in producing moon rover training data

I had a interesting chat with some folks working on autonomous moon rover tech. One of the limitations is training data as there are very few images taken from the surface of the moon. The moon also has a surprising variety of landscapes.

I considered a few solutions but ended up deciding on the following approach.

 - Programatically generate moonscape models (using Blender's python API)
 - Render multiple images for each model at heights of ~1.5m (I'm assuming that most of the moon images were take around this height)
 - Use [Llava](https://ollama.com/library/llava) to compare my rendered image to existing moon images

This approach has the benefit of producing 3d models with realistic moon features that vision models can actually navigate.
