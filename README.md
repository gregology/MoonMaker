# MoonMaker

## A procedural lunar surface generator for autonomous rover training

I had an interesting chat with some folks developing autonomous rover tech for use on the lunar and martian surfaces. One of the problems they face is the lack of accurate training data. There are very few images from places like the lunar surface. The few images that do exist of the lunar surface are not directly useful as training data for rover imaging systems because the images are;

 - a biassed sample (astronauts likely focused their cameras on the most interesting landscape features)
 - not at the right perspective for a rover (likely taken from the height of the astronauts or a tripod, ~1.5m)
 - 2D representations of 3D environments (which makes it difficult to create success metrics)

As a proof of concept I decided to use the existing lunar surface images as references to produce more accurate 3D lunar surface models. I created a procedural lunar surface generator using the Blender Python API. The procedural lunar surface generator accepts density attributes for rocks, craters, small craters, hills, and depressions. I then generated multiple 3D models with different density attributes and rendered images at a similar height as a reference image. Finally I used a multimodal model to score the likeness in topology between the rendered images and the reference images.

With this process we can fine tune the attributes for the procedural lunar surface generator to create realistic 3D models for training autonomous rovers. Having realistic 3D surface lunar models allow the vision models to navigate at realistic perspectives, camera angles, and in differing lighting conditions. Training in a 3D model environment also means the rover imaging systems can receive useful feedback when it navigates into unsuitable areas like steep embankments.

This approach makes training relatively cheap so multiple models can be produced. A rover could store multiple versions of the vision model and use the best option depending on the area the rover is exploring, the current lunar phase, degradation of the camera, lens flare artifacts, etc.

## Results

#### Reference image
![image](https://github.com/gregology/MoonMaker/assets/1595448/fe279878-80fa-40e6-979e-8af5b0116733)

#### High scoring rendered image
![image](https://github.com/gregology/MoonMaker/assets/1595448/6d68b9f1-1c1e-4bd1-a978-e4f8809a2a85)

#### High scoring model
![image](https://github.com/gregology/MoonMaker/assets/1595448/9e27c42e-d28b-401c-9c6c-66e0f7926c39)

#### Low scoring model
![image](https://github.com/gregology/MoonMaker/assets/1595448/728d0f4c-b692-4297-afd8-78889cf6fb20)

## Future development

This was a quick proof of concept. Here are some things I need to fix / think about for future development.

### Terrestrial testing

The effectiveness of this technique as training data could be tested on Earth by taking similar biassed reference images from a terrestrial landscape, creating a procedural surface generator, training a vision model, and seeing how successfully it navigates the real terrestrial environment.

### Prompt engineering for image scoring

I'm currently making two separate Ollama API calls to determine how close the rendered images relate to the reference image. Firstly I send the reference image and rendered image to [Llava 13b](https://llava-vl.github.io/) to retrieve analysis on the differences and then I use [miqu 70b](https://huggingface.co/miqudev/miqu-1-70b) convert the analysis to a number between 0 and 1. Llava is limited and doesn't follow instructions very well but there may be some other prompting techniques I can use to get the image scoring from a single prompt given to Llava. There are also some [Llava/Mistral hybrid options](https://huggingface.co/liuhaotian/llava-v1.6-mistral-7b) that would be worth investigating.

### Abstracting Logic from Blender Python Script

The `create_moon_model()` function should be callable from outside the Blender script. Creating the moon models and generating the renders should be separated to best utilize resources. I need to update the [Blender API Flask app](https://github.com/gregology/blender_api) to accept variables and add a delete endpoint for removing retrieved models and possibly a status endpoint with details about GPU and CPU utilization. This abstraction will simplify the code and has additional advantages such as:

- Utilizing multi-threading, as the Blender Python API currently utilizes only a single core.
- Enhancing resilience, especially with more complex models.

### Reference videos

I only used reference photos however there is video footage from the lunar surface which may be useful reference material.

### Utilise existing 3D models and rock samples

Detailed 3D models of the lunar surface taken from lunar orbit already exist. We could use these models to create more accurate topology. We could also use 3D models of lunar rock samples to add accurate textures.

### Details of reference images

Knowing exactly when and where images were taken would allow us to accurately mimic the environment as it was when the photo was taken. This would generate more accurate results with less GPU cycles.

## Bugs

 - Shadows do not fall as expected in some rendered images.
 - The `surface_height()` function does not work well on areas with steep inclines. This is causing some images to be rendered subterranean.
 - Steep inclines can also cause rocks to float. I need to introduce a clean up process to remove any objects that are not connected to the main plane.

## Training hardware

I used two GPUs to process the data;

 - RTX4090 in my gaming / ML rig running Ollama for the image rating
 - RX 5600XT in an eGPU enclosure running a [Blender API Flask app](https://github.com/gregology/blender_api) I created for this purpose

## Alternative solutions to generate training data

### Lunar image style transfer

Generate an image-to-image lunar translation which converts images of terrestrial landscape into realistic renderings of lunar landscape. A rover's video feed could be routed through this image-to-image lunar translation when being trained on Earth. Alternatively, this approach could be used to test the training performance of the procedural lunar surface generator in real world situations.
