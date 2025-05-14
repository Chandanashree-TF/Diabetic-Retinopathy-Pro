from ultralytics import YOLO


model = YOLO('yolo11n.pt')
# Set up training parameters
model.train(data='datasets/data.yaml', epochs=10,imgsz=440,batch=2 ,workers=4, cache=True, amp=True)
