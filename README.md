# MoonMaker

## An experiment in producing moon rover training data

I had an interesting chat with some folks working on autonomous moon rover tech. One of the limitations is training data as there are very few images taken from the surface of the moon. The moon also, has a surprising variety of landscapes.

The two most promising solutions I came up with were;
 - Adding AI filters to video from rocky earth landscapes to make them appear like the lunar surface
 - Creating realistic 3D moon surface models and using generative AI to finetune them

Here is my approach for the second solution;
 - Programmatically generate moonscape models (using Blender's python API)
 - Render multiple images for each model at heights of ~1.5m (I'm assuming that most of the moon images were taken around this height)
 - Use [Llava](https://ollama.com/library/llava) to compare my rendered image to existing moon images
   - Additionally Llava can help tune the arguments used to render the models (more rocks, less crators, etc)

This approach has the benefit of producing 3D models with realistic moon features that vision models can actually navigate.

## Moonscape Comparisons

#### Actual Moonscape

![image](https://github.com/gregology/MoonMaker/assets/1595448/95e1b2e5-97a3-49a8-9577-69f8da2f12b7)

Note: There is significant bias in our moonscape sample data as;
 - Spacecraft that lands on the moon chooses flatter areas to maximise successful landing
 - Humans are more likely to take photos of novel landscapes
 - The quality of vision sensors continue to change

#### Rendered Moonscape

![image](https://github.com/gregology/MoonMaker/assets/1595448/a71dc3b7-cce8-4b0d-a3c4-e4319ffa19b8)

Note: The contrast is wrong as the sky is too light and the ground is too dark. Blender is also introducing a haze during the rendering process. The ground is too flat.
