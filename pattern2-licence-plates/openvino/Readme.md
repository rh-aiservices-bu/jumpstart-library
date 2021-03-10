- Download model
```
curl --create-dirs https://download.01.org/opencv/2021/openvinotoolkit/2021.1/open_model_zoo/models_bin/1/vehicle-license-plate-detection-barrier-0106/FP32/vehicle-license-plate-detection-barrier-0106.bin  https://download.01.org/opencv/2021/openvinotoolkit/2021.1/open_model_zoo/models_bin/1/vehicle-license-plate-detection-barrier-0106/FP32/vehicle-license-plate-detection-barrier-0106.xml -o model/vehicle-license-plate-detection/1/vehicle-license-plate-detection-barrier-0106.bin -o  model/vehicle-license-plate-detection/1/vehicle-license-plate-detection-barrier-0106.xml
```
- Run model locally
```
docker run -d -u $(id -u):$(id -g) --name vehicle-license-plate-detection -v $(pwd)/model:/models/vehicle-license-plate-detection -p 9000:9000  -p 8000:8000 openvino/model_server:latest --model_path /models/vehicle-license-plate-detection --model_name vehicle-license-plate-detection --port 9000 --rest_port 8000 --log_level DEBUG --shape auto
```

- Submit sample image to validate model
```
python rest_serving_client.py --image_path images/car1.jpg --rest_port 8000 --model_name "vehicle-license-plate-detection" --model_version 1 --transpose_input False
```
- Results
```
 ✘ karasing@karans-MacBook-Pro  ~/git/jumpstart-library/pattern2-licence-plates/openvino   ksingh-openvino  python rest_serving_client.py --image_path images/car1.jpg --rest_port 8000 --model_name "vehicle-license-plate-detection" --model_version 1 --transpose_input False
[[[[ 15  41 100 ...  23  24   6]
   [ 18  26 103 ...  15  43  14]
   [ 16  70 114 ...  11  52  23]
   ...
   [158 146 152 ... 172 163 159]
   [144 159 154 ... 155 179 157]
   [139 155 156 ... 172 176 168]]

  [[ 99 105 127 ...  34  34  12]
   [116 104 139 ...  24  57  24]
   [107 117 145 ...  17  70  37]
   ...
   [156 144 150 ... 172 163 159]
   [142 157 152 ... 155 179 157]
   [137 154 156 ... 173 178 168]]

  [[165 161 163 ...  40  46   8]
   [186 166 176 ...  26  76  25]
   [178 165 180 ...  17  94  44]
   ...
   [156 144 150 ... 172 163 159]
   [142 157 152 ... 155 179 157]
   [137 154 155 ... 171 175 168]]]]
('Image data range:', 0, ':', 255)
Start processing:
	Model name: vehicle-license-plate-detection
	Iterations: 2
	Images numpy path: None
	Images in shape: (2, 3, 300, 300)

output shape: (1, 1, 200, 7)
Iteration 1; Processing time: 52.74 ms; speed 18.96 fps
imagenet top results in a single batch:
('\t', 0, 'bald eagle, American eagle, Haliaeetus leucocephalus', 22, '')
output shape: (1, 1, 200, 7)
Iteration 2; Processing time: 44.74 ms; speed 22.35 fps
imagenet top results in a single batch:
('\t', 0, 'bald eagle, American eagle, Haliaeetus leucocephalus', 22, '')
```