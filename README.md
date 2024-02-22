# MoonMaker

## A procedural lunar surface generator for autonomous rover training

I had an interesting chat with some folks developing autonomous rover tech for use on the lunar and martian surfaces. One of the problems they face is the lack of accurate training data. There are very few images from places like the lunar surface. The few images that do exist of the lunar surface are not directly useful as training data for rover imaging systems because the images are;

 - a biassed sample (astronauts likely focused their cameras on the most interesting landscape features)
 - not at the right perspective for a rover (likely taken at heights ~1.5m)
 - 2D representations of 3D environments (which makes it difficult to create success metrics)

As a proof of concept I decided to use the existing lunar surface images as references to produce more accurate 3D lunar surface models. I created a procedural lunar surface generator using the Blender Python API. The procedural lunar surface generator accepts density attributes for rocks, craters, small craters, hills, and depressions. I then generated multiple 3D models with different density attributes and rendered images at a similar height as a reference image. Finally I used a multimodal model to score the likeness in topology between the rendered images and the reference images.

With this process we can fine tune the attributes for the procedural lunar surface generator to create realistic 3D models for training autonomous rovers. Having realistic 3D surface lunar models allow the vision models to navigate at realistic perspectives, camera angles, and in differing lighting conditions. Training in a 3D model environment also means the rover imaging systems can receive useful feedback when it navigates into unsuitable areas like steep embankments.

## Results

incoming....

## Training hardware

I used two GPUs to process the data;

 - RTX4090 in my gaming / ML rig running Ollama for the multimodal model / LLM
 - RX 5600 XT in an eGPU enclosure running a [Blender API Flask app](https://github.com/gregology/blender_api) I created for this purpose

## Future development

This was a quick proof of concept. Here are some things I need to fix / think about for future development

### Terrestrial testing

The effectiveness of this technique as training data could be tested on Earth by taking similar biassed reference images from a terrestrial landscape, creating a procedural surface generator, training a vision model, and seeing how successfully it navigates the real terrestrial environment.

### Reference videos

I only used reference photos however there is video footage from the lunar surface which may be useful reference material.

### Utilise existing 3D models and rock samples

Detailed 3D models of the lunar surface taken from lunar orbit already exist. We could use these models to create more accurate topology. We could also use 3D models of lunar rock samples to add accurate textures.

### Details of reference images

Knowing exactly when and where images were taken would allow us to accurately mimic the environment as it was when the photo was taken. This would generate more accurate results with less GPU cycles.

## Bugs

 - Shadows do not fall as expected in some rendered images
