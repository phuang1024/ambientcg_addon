rm -rf ./build
mkdir -p ./build
cp -r ./src ./build/ambientcg
cd ./build
rm -rf ./ambientcg/__pycache__
zip -r ./ambientcg.zip ./ambientcg
