// Reproducible synthetic colour-card model. Not a trained hand recognizer.
const tf=require('@tensorflow/tfjs');const fs=require('node:fs');const path=require('node:path');
(async()=>{
 const labels=['ATTACK','SHIELD','HEAL','IDLE'];
 const make=size=>{const m=tf.sequential();m.add(tf.layers.globalAveragePooling2d({inputShape:[size,size,3]}));m.add(tf.layers.dense({units:16,activation:'relu',kernelInitializer:tf.initializers.glorotUniform({seed:41})}));m.add(tf.layers.dense({units:4,activation:'softmax',kernelInitializer:tf.initializers.glorotUniform({seed:42})}));return m;};
 const m=make(1);m.compile({optimizer:tf.train.adam(.035),loss:'categoricalCrossentropy',metrics:['accuracy']});
 let seed=99;const rand=()=>{seed=(1664525*seed+1013904223)>>>0;return seed/4294967296;};
 const x=[],y=[];
 for(let c=0;c<4;c++)for(let i=0;i<100;i++){
  const low=.04+rand()*.25,high=.65+rand()*.35,gray=.03+rand()*.94;
  const rgb=c===0?[high,low,low]:c===1?[low,low,high]:c===2?[low,high,low]:[gray,gray,gray];x.push(rgb.map(v=>v*255/127-1));y.push(labels.map((_,j)=>j===c?1:0));
 }
 const xs=tf.tensor4d(x.flat(),[400,1,1,3]),ys=tf.tensor2d(y);
 const h=await m.fit(xs,ys,{epochs:90,batchSize:40,shuffle:false,verbose:0});
 const final=make(224);final.setWeights(m.getWeights());
 const folder=path.resolve('teacher/demo-model');fs.mkdirSync(folder,{recursive:true});
 await final.save(tf.io.withSaveHandler(async a=>{
  const metadata={tfjsVersion:tf.version.tfjs,packageVersion:'0.8.5',packageName:'@teachablemachine/image',modelName:'Synthetic colour cards — not hands',labels,imageSize:224};
  const spec={format:'layers-model',generatedBy:'TensorFlow.js '+tf.version.tfjs,convertedBy:null,modelTopology:a.modelTopology,weightsManifest:[{paths:['weights.bin'],weights:a.weightSpecs}]};
  fs.writeFileSync(path.join(folder,'model.json'),JSON.stringify(spec));fs.writeFileSync(path.join(folder,'metadata.json'),JSON.stringify(metadata));fs.writeFileSync(path.join(folder,'weights.bin'),Buffer.from(a.weightData));
  fs.writeFileSync(path.join(folder,'bundle.json'),JSON.stringify({modelTopology:a.modelTopology,weightSpecs:a.weightSpecs,weightData:Buffer.from(a.weightData).toString('base64'),metadata}));
  return {modelArtifactsInfo:{dateSaved:new Date(),modelTopologyType:'JSON'}};
 }));
 console.log('Trained synthetic colour model: accuracy',h.history.acc.at(-1));
 for(const [c,rgb] of [[0,[255,0,0]],[1,[0,0,255]],[2,[0,255,0]],[3,[127,127,127]]]){const input=tf.tensor4d(rgb.map(v=>v/127-1),[1,1,1,3]);const out=await m.predict(input).data();if(out[c]<.85)throw Error('Fixture accuracy failure '+labels[c]);input.dispose();}
 xs.dispose();ys.dispose();m.dispose();final.dispose();
})();
