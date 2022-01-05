
%%bash
git clone https://github.com/pytorch/vision.git
cd vision
git checkout v0.3.0
cp references/detection/utils.py ../
cp references/detection/transforms.py ../
cp references/detection/coco_eval.py ../
cp references/detection/engine.py ../
cp references/detection/coco_utils.py ../


cd references

cd detection


python engine.py install
python coco_eval.py install
python coco_utils.py install
python transforms.py install
python utils.py install