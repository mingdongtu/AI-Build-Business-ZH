// Mock data for testing frontend components
export const mockAnalysisResult = {
  food_name: "康师傅红烧牛肉面",
  ingredients: [
    "小麦粉", "棕榈油", "食用盐", "碳酸钠", "碳酸钾", 
    "牛肉", "大豆油", "白砂糖", "味精", "酱油", 
    "香辛料", "食品添加剂", "柠檬酸", "焦糖色素"
  ],
  score: 65,
  health_points: [
    { type: "positive", description: "含有优质蛋白质" },
    { type: "negative", description: "含有较高钠含量" },
    { type: "negative", description: "含有食品添加剂" },
    { type: "positive", description: "碳水化合物含量适中" }
  ],
  recommendations: ["建议适量食用，搭配新鲜蔬菜", "注意控制钠的摄入量"],
  detailed_analysis: {
    positive_aspects: ["提供能量", "含有蛋白质"],
    negative_aspects: ["钠含量高", "含有添加剂"],
    nutritional_highlights: ["碳水化合物", "蛋白质", "脂肪"]
  },
  processing_time: 1.25,
  extracted_text: "配料：小麦粉、棕榈油、食用盐、碳酸钠、碳酸钾、牛肉、大豆油、白砂糖、味精、酱油、香辛料、食品添加剂、柠檬酸、焦糖色素",
  extracted_text_length: 72,
  ocr_success: true
};

export const mockOcrFailureResult = {
  food_name: "",
  ingredients: [],
  score: 0,
  health_points: [],
  recommendations: ["无法识别配料表，请手动输入"],
  processing_time: 0.75,
  extracted_text: "",
  extracted_text_length: 0,
  ocr_success: false
};

export const mockManualInputResult = {
  food_name: "自定义食品",
  ingredients: [
    "小麦粉", "白砂糖", "植物油", "鸡蛋", "奶粉", 
    "泡打粉", "香精", "食用盐"
  ],
  score: 70,
  health_points: [
    { type: "positive", description: "含有优质蛋白质" },
    { type: "negative", description: "含有较高糖分" },
    { type: "positive", description: "脂肪含量适中" }
  ],
  recommendations: ["建议适量食用，控制每日糖分摄入"],
  detailed_analysis: {
    positive_aspects: ["提供能量", "含有蛋白质"],
    negative_aspects: ["糖分含量高"],
    nutritional_highlights: ["碳水化合物", "蛋白质", "脂肪"]
  },
  processing_time: 0.95,
  extracted_text: "小麦粉、白砂糖、植物油、鸡蛋、奶粉、泡打粉、香精、食用盐",
  extracted_text_length: 32,
  manual_input: true
};
