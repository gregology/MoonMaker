# MoonMaker

## An experiment in producing moon rover training data

I had an interesting chat with some folks working on autonomous moon rover tech. One of the limitations is training data as there are very few images taken from the surface of the moon. The moon also has a surprising variety of landscapes.

I considered a few solutions but ended up deciding on the following approach.

 - Programmatically generate moonscape models (using Blender's python API)
 - Render multiple images for each model at heights of ~1.5m (I'm assuming that most of the moon images were taken around this height)
 - Use [Llava](https://ollama.com/library/llava) to compare my rendered image to existing moon images

This approach has the benefit of producing 3D models with realistic moon features that vision models can actually navigate.

## Moonscape Comparisons

#### Actual

![image](https://github.com/gregology/MoonMaker/assets/1595448/95e1b2e5-97a3-49a8-9577-69f8da2f12b7)

Note: There is significant bias in our moonscape sample data as;
 - spacecraft that lands on the moon chooses flatter areas to maximise successful landing
 - humans are more likely to take photos of novel landscapes
 - the quality of vision sensors continue to change

#### Rendered

![image](https://github.com/gregology/MoonMaker/assets/1595448/a71dc3b7-cce8-4b0d-a3c4-e4319ffa19b8)

Note: The contrast is off as the sky is too light and the ground is too dark. Blender is also introducing a haze during the rendering process. The ground is too flat.
