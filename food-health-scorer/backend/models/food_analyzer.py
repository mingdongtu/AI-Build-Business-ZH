import logging
import re
from typing import List, Dict, Any, Union, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

class FoodAnalyzer:
    """
    Class for analyzing food ingredients and calculating health scores
    with comprehensive scoring rules and scientific reasoning
    """
    
    def __init__(self):
        # Set up logger
        self.logger = logging.getLogger('FoodAnalyzer')
        
        # Dictionary of common ingredients and their health impact with scientific reasoning
        # Format: ingredient: (score, scientific_reason)
        self.ingredient_data = {
            # === UNHEALTHY INGREDIENTS ===
            # Sugars
            "糖": (-10, "精制糖会导致血糖快速升高，与肥胖、2型糖尿病和心血管疾病风险增加相关"),
            "白砂糖": (-10, "精制糖会导致血糖快速升高，与肥胖、2型糖尿病和心血管疾病风险增加相关"),
            "蔗糖": (-8, "精制糖会导致血糖快速升高，与肥胖和代谢综合征相关"),
            "葡萄糖": (-5, "单糖，血糖指数高，会导致血糖快速升高"),
            "果糖": (-6, "过量摄入与非酒精性脂肪肝、胰岛素抵抗和肥胖相关"),
            "麦芽糊精": (-5, "高度加工的碳水化合物，血糖指数高"),
            "玉米糖浆": (-8, "高度加工的甜味剂，含有大量果糖和葡萄糖"),
            "高果糖玉米糖浆": (-12, "含有高浓度果糖，与肥胖、代谢综合征和脂肪肝相关性更强"),
            "转化糖浆": (-8, "蔗糖经水解形成的葡萄糖和果糖混合物，血糖指数高"),
            "糖浆": (-7, "浓缩糖溶液，会导致血糖快速升高"),
            "红糖": (-4, "比白砂糖含有少量矿物质，但仍是添加糖"),
            "冰糖": (-8, "精制蔗糖结晶，与白砂糖类似"),
            
            # Unhealthy Fats
            "反式脂肪": (-15, "增加低密度脂蛋白(LDL)胆固醇，降低高密度脂蛋白(HDL)胆固醇，增加心脏病风险"),
            "氢化植物油": (-12, "含有反式脂肪，增加心血管疾病风险"),
            "部分氢化植物油": (-12, "含有反式脂肪，增加心血管疾病风险"),
            "人造奶油": (-8, "可能含有反式脂肪和饱和脂肪"),
            "起酥油": (-8, "高饱和脂肪含量，可能含有反式脂肪"),
            "棕榈油": (-6, "高饱和脂肪含量，可能增加心血管疾病风险"),
            "椰子油": (-5, "高饱和脂肪含量，但含有中链脂肪酸，健康影响存在争议"),
            "猪油": (-7, "高饱和脂肪含量，可能增加心血管疾病风险"),
            "牛油": (-6, "高饱和脂肪含量，可能增加心血管疾病风险"),
            
            # Flavor Enhancers
            "味精": (-3, "谷氨酸钠，可能导致部分人群出现头痛、心悸等'中式餐厅综合征'症状"),
            "谷氨酸钠": (-3, "可能导致部分人群出现头痛、心悸等'中式餐厅综合征'症状"),
            "鸟苷酸二钠": (-2, "增味剂，与谷氨酸钠协同增强鲜味"),
            "肌苷酸二钠": (-2, "增味剂，与谷氨酸钠协同增强鲜味"),
            
            # Preservatives
            "防腐剂": (-5, "长期摄入某些防腐剂可能影响肠道菌群和代谢健康"),
            "苯甲酸钠": (-5, "可能引起过敏反应，高浓度时可能对肝脏有害"),
            "山梨酸钾": (-4, "相对安全的防腐剂，但可能引起过敏反应"),
            "脱氢乙酸": (-5, "可能影响肠道菌群，高剂量可能有毒性"),
            "亚硝酸盐": (-8, "可能在体内转化为亚硝胺，亚硝胺是已知的致癌物"),
            "亚硫酸盐": (-5, "可能引起哮喘患者和敏感人群的不良反应"),
            "二氧化硫": (-5, "可能引起过敏反应和呼吸系统刺激"),
            "丙酸钙": (-3, "相对安全的防腐剂，但长期大量摄入的影响未明确"),
            
            # Artificial Additives
            "人工色素": (-5, "可能与儿童多动症和过敏反应相关"),
            "人工香料": (-5, "可能引起头痛和过敏反应"),
            "增稠剂": (-3, "可能影响肠道菌群和消化过程"),
            "乳化剂": (-3, "某些乳化剂可能影响肠道屏障功能和菌群"),
            "稳定剂": (-2, "长期影响未明确，但属于高度加工食品成分"),
            "抗氧化剂": (-1, "部分合成抗氧化剂可能有健康隐患"),
            "甜味剂": (-4, "人工甜味剂可能影响肠道菌群和代谢"),
            
            # Specific Artificial Sweeteners
            "甜蜜素": (-6, "人工甜味剂，可能影响肠道菌群和血糖调节"),
            "安赛蜜": (-5, "人工甜味剂，长期健康影响存在争议"),
            "糖精": (-6, "最早的人工甜味剂，安全性存在争议"),
            "阿斯巴甜": (-5, "人工甜味剂，可能引起某些敏感人群的不良反应"),
            "三氯蔗糖": (-5, "人工甜味剂，可能影响肠道菌群"),
            "甜菊糖苷": (-2, "天然来源的甜味剂，相对较安全但长期影响未明确"),
            
            # === NEUTRAL INGREDIENTS ===
            "盐": (-2, "适量摄入是必要的，但过量与高血压相关"),
            "食用盐": (-2, "适量摄入是必要的，但过量与高血压相关"),
            "水": (0, "基本成分，无健康影响"),
            "小麦粉": (0, "基本碳水化合物来源，但精制小麦粉缺乏膳食纤维"),
            "面粉": (0, "基本碳水化合物来源，但精制面粉缺乏膳食纤维"),
            "大豆油": (0, "含有必需脂肪酸，但高度精制过程可能产生不良物质"),
            "植物油": (0, "提供必需脂肪酸，但高度精制过程可能产生不良物质"),
            "玉米油": (0, "含有一定不饱和脂肪酸，但omega-6与omega-3比例失衡"),
            "葵花籽油": (1, "含有维生素E和不饱和脂肪酸"),
            "鸡蛋": (2, "提供优质蛋白质和多种营养素"),
            "牛奶": (2, "提供蛋白质、钙和维生素D"),
            "淀粉": (-1, "精制碳水化合物，可能导致血糖波动"),
            "食用香精": (-3, "可能含有多种化学合成物质"),
            
            # === HEALTHY INGREDIENTS ===
            # Whole Grains
            "全麦粉": (8, "含有更多膳食纤维、维生素和矿物质，有助于稳定血糖"),
            "全谷物": (9, "含有丰富的膳食纤维、抗氧化物和营养素"),
            "燕麦": (10, "含有β-葡聚糖，有助于降低胆固醇和稳定血糖"),
            "糙米": (8, "保留了胚芽和麸皮，含有更多膳食纤维和营养素"),
            "藜麦": (9, "完整蛋白质来源，含有所有必需氨基酸和丰富矿物质"),
            "荞麦": (8, "无麸质全谷物，含有优质蛋白质和抗氧化物"),
            
            # Legumes
            "大豆": (7, "优质植物蛋白来源，含有异黄酮，可能有助于心血管健康"),
            "豆类": (7, "富含蛋白质、膳食纤维和多种维生素矿物质"),
            "黑豆": (8, "富含抗氧化物和膳食纤维"),
            "红豆": (7, "富含膳食纤维和铁"),
            "绿豆": (7, "低热量，富含蛋白质和抗氧化物"),
            "鹰嘴豆": (7, "富含蛋白质、膳食纤维和叶酸"),
            
            # Nuts and Seeds
            "坚果": (8, "富含健康脂肪、蛋白质和多种微量元素"),
            "杏仁": (8, "富含维生素E、镁和健康脂肪"),
            "核桃": (9, "含有omega-3脂肪酸，有益大脑健康"),
            "花生": (5, "富含蛋白质和不饱和脂肪，但可能含有黄曲霉毒素"),
            "亚麻籽": (10, "富含omega-3脂肪酸、膳食纤维和木酚素"),
            "奇亚籽": (10, "富含omega-3脂肪酸、蛋白质和抗氧化物"),
            "南瓜籽": (8, "富含锌、镁和健康脂肪"),
            "向日葵籽": (7, "富含维生素E和硒"),
            
            # Healthy Oils
            "橄榄油": (8, "富含单不饱和脂肪酸和抗氧化物，有益心血管健康"),
            "亚麻籽油": (9, "极佳的植物性omega-3脂肪酸来源"),
            "鳄梨油": (8, "富含单不饱和脂肪酸和维生素E"),
            
            # Natural Sweeteners (in moderation)
            "蜂蜜": (2, "比精制糖含有更多抗氧化物和酶，但仍是糖"),
            "枣泥": (3, "天然甜味，含有一定膳食纤维和矿物质"),
            "龙舌兰糖浆": (1, "低血糖指数，但仍是添加糖"),
            "椰子糖": (1, "含有少量矿物质，但仍是糖"),
            
            # Fruits and Vegetables
            "水果": (8, "富含维生素、矿物质、抗氧化物和膳食纤维"),
            "蔬菜": (10, "低热量，富含维生素、矿物质、抗氧化物和膳食纤维"),
            "菠菜": (10, "富含铁、叶酸和抗氧化物"),
            "胡萝卜": (8, "富含β-胡萝卜素和纤维"),
            "西兰花": (10, "富含维生素C、K和抗癌化合物"),
            "番茄": (8, "富含番茄红素和维生素C"),
            "蓝莓": (9, "富含花青素和抗氧化物"),
            "苹果": (7, "富含果胶纤维和抗氧化物"),
            
            # Protein Sources
            "鸡肉": (5, "瘦肉蛋白质来源，脂肪含量相对较低"),
            "鱼": (7, "富含优质蛋白质和omega-3脂肪酸"),
            "三文鱼": (9, "极佳的omega-3脂肪酸来源"),
            "豆腐": (6, "优质植物蛋白来源，含有异黄酮"),
            
            # Fermented Foods
            "酸奶": (6, "含有益生菌，有助于肠道健康"),
            "乳酸菌": (7, "有助于维持肠道菌群平衡"),
            "益生菌": (7, "有助于肠道健康和免疫功能"),
            "泡菜": (5, "发酵食品，含有益生菌，但可能含盐量高"),
            "醋": (3, "可能有助于稳定餐后血糖"),
            
            # Functional Ingredients
            "膳食纤维": (10, "有助于肠道健康、稳定血糖和降低胆固醇"),
            "燕麦纤维": (9, "可溶性纤维，有助于降低胆固醇"),
            "菊粉": (8, "益生元，促进有益肠道菌群生长"),
            "抗性淀粉": (7, "有助于肠道健康和血糖管理"),
            "绿茶提取物": (6, "富含抗氧化儿茶素"),
            "姜黄素": (6, "具有抗炎特性"),
            "螺旋藻": (7, "富含蛋白质和多种营养素"),
            "大麦草": (6, "富含叶绿素和抗氧化物")
        }
        
        # Extract scores for easier lookup
        self.ingredient_scores = {k: v[0] for k, v in self.ingredient_data.items()}
        
        # Additives that are concerning with scientific reasoning
        self.concerning_additives = {
            "甜蜜素": "可能影响肠道菌群平衡，长期使用的安全性存在争议",
            "安赛蜜": "人工甜味剂，可能影响肠道菌群和葡萄糖耐受性",
            "糖精": "最早的人工甜味剂，在高剂量下可能有致癌风险",
            "阿斯巴甜": "可能引起某些敏感人群的头痛和过敏反应",
            "三氯蔗糖": "可能影响肠道菌群和胰岛素敏感性",
            "丙二醇": "食品保湿剂，大剂量可能对肾脏和肝脏有影响",
            "二氧化硫": "可能引起哮喘患者的不良反应和呼吸系统刺激",
            "亚硫酸盐": "可能引起过敏反应，尤其是哮喘患者",
            "硝酸盐": "可能转化为亚硝酸盐，进而形成亚硝胺",
            "亚硝酸盐": "可能在体内形成亚硝胺，亚硝胺是已知的致癌物",
            "苯甲酸": "可能引起过敏反应，高浓度时可能对肝脏有害",
            "山梨酸": "相对安全的防腐剂，但可能引起皮肤刺激和过敏",
            "脱氢乙酸": "可能影响肠道菌群，高剂量可能有毒性",
            "纳他霉素": "抗真菌防腐剂，长期影响未明确",
            "胭脂红": "可能引起过敏反应和多动症",
            "日落黄": "可能引起过敏反应和行为问题",
            "柠檬黄": "可能引起过敏反应和行为问题",
            "靛蓝": "可能引起过敏反应和行为问题",
            "亮蓝": "可能引起过敏反应和行为问题",
            "焦糖色": "高温处理的糖，可能含有潜在致癌物质",
            "二氧化钛": "食品着色剂，可能积累在体内",
            "聚山梨酯80": "乳化剂，可能影响肠道屏障功能",
            "羧甲基纤维素": "增稠剂，可能影响肠道菌群",
            "邻苯二甲酸酯": "塑化剂，可能是内分泌干扰物"
        }
    
    def analyze(self, ingredients):
        """
        Analyze ingredients and return health score and analysis with scientific reasoning
        
        Args:
            ingredients (list): List of ingredient strings
        
        Returns:
            dict: Analysis result with score, details, and scientific reasoning
        """
        self.logger.info(f"Analyzing {len(ingredients)} ingredients")
        
        if not ingredients:
            self.logger.warning("No ingredients provided for analysis")
            return {
                "score": 0,
                "health_points": [],
                "recommendations": ["No ingredients provided for analysis."],
                "scientific_reasoning": ["Analysis requires ingredient information to evaluate nutritional impact."]
            }
        
        # Initialize score and tracking variables
        score = 50  # Start with a neutral score
        health_points = []
        recommendations = []
        scientific_reasoning = []
        
        # Count ingredients and track metrics
        total_ingredients = len(ingredients)
        scored_ingredients = 0
        additives_count = 0
        sugar_count = 0
        unhealthy_fat_count = 0
        artificial_additive_count = 0
        whole_food_count = 0
        healthy_ingredient_count = 0
        preservative_count = 0
        
        # Track ingredient impacts with scientific reasoning
        positive_impacts = []
        negative_impacts = []
        additive_impacts = []
        
        # Ingredient categories for analysis
        sugars = ["糖", "白砂糖", "蔗糖", "葡萄糖", "果糖", "玉米糖浆", "高果糖玉米糖浆", "转化糖浆"]
        unhealthy_fats = ["反式脂肪", "氢化植物油", "部分氢化植物油", "人造奶油", "起酥油"]
        artificial_additives = ["人工色素", "人工香料", "甜味剂", "甜蜜素", "安赛蜜", "糖精"]
        whole_foods = ["全麦", "全谷物", "燕麦", "糙米", "藜麦", "蔬菜", "水果", "坚果", "豆类"]
        
        # Analyze each ingredient
        for ingredient in ingredients:
            ingredient = ingredient.strip()
            if not ingredient:
                continue
                
            # Check if ingredient is in our database with scientific reasoning
            matched = False
            for known_ingredient, data in self.ingredient_data.items():
                if known_ingredient in ingredient:
                    impact, reason = data
                    score += impact
                    scored_ingredients += 1
                    
                    # Categorize the ingredient
                    if any(sugar in known_ingredient for sugar in sugars):
                        sugar_count += 1
                    elif any(fat in known_ingredient for fat in unhealthy_fats):
                        unhealthy_fat_count += 1
                    elif any(additive in known_ingredient for additive in artificial_additives):
                        artificial_additive_count += 1
                    elif any(food in known_ingredient for food in whole_foods):
                        whole_food_count += 1
                    
                    if impact > 0:
                        healthy_ingredient_count += 1
                        positive_impacts.append((ingredient, impact, reason))
                    elif impact < 0:
                        negative_impacts.append((ingredient, impact, reason))
                    
                    matched = True
                    break
            
            # Check for concerning additives with scientific reasoning
            for additive, reason in self.concerning_additives.items():
                if additive in ingredient:
                    additives_count += 1
                    preservative_count += 1
                    additive_impacts.append((additive, reason))
                    matched = True
                    break
        
        # Adjust score based on proportion of scored ingredients
        if total_ingredients > 0 and scored_ingredients / total_ingredients < 0.5:
            score -= 10
            health_points.append("Many ingredients could not be recognized or scored (-10 points)")
            scientific_reasoning.append("Unknown ingredients may contain hidden additives or processing aids not listed specifically.")
        
        # Penalize for additives with scientific reasoning
        if additives_count > 0:
            # Progressive penalty that increases with more additives
            additive_penalty = min(5 + (additives_count * 3), 25)  # Base penalty + scaling, capped at -25
            score -= additive_penalty
            health_points.append(f"Contains {additives_count} concerning additives (-{additive_penalty} points)")
            scientific_reasoning.append("Multiple food additives may have synergistic negative effects on gut microbiome and metabolic health.")
        
        # Analyze ingredient distribution and apply additional rules
        ingredient_analysis = self._analyze_ingredient_distribution(
            total_ingredients, sugar_count, unhealthy_fat_count, 
            artificial_additive_count, whole_food_count, healthy_ingredient_count,
            preservative_count
        )
        
        # Apply distribution-based score adjustments
        score += ingredient_analysis["score_adjustment"]
        health_points.extend(ingredient_analysis["health_points"])
        scientific_reasoning.extend(ingredient_analysis["scientific_reasoning"])
        
        # Add health points based on impacts with scientific reasoning
        positive_impacts.sort(key=lambda x: x[1], reverse=True)
        negative_impacts.sort(key=lambda x: x[1])
        
        # Add top positive impacts with scientific reasoning
        for ingredient, impact, reason in positive_impacts[:3]:
            health_points.append(f"{ingredient} is beneficial (+{impact} points)")
            scientific_reasoning.append(f"{ingredient}: {reason}")
        
        # Add top negative impacts with scientific reasoning
        for ingredient, impact, reason in negative_impacts[:3]:
            health_points.append(f"{ingredient} is concerning ({impact} points)")
            scientific_reasoning.append(f"{ingredient}: {reason}")
        
        # Generate recommendations based on comprehensive analysis
        recommendations_list, additional_reasoning = self._generate_recommendations(
            score, sugar_count, unhealthy_fat_count, artificial_additive_count,
            whole_food_count, additive_impacts
        )
        recommendations.extend(recommendations_list)
        scientific_reasoning.extend(additional_reasoning)
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        self.logger.info(f"Analysis complete. Final health score: {score}")
        
        return {
            "score": score,
            "health_points": health_points,
            "recommendations": recommendations,
            "scientific_reasoning": scientific_reasoning
        }
    
    def get_ingredient_info(self, ingredient):
        """
        Get detailed information about a specific ingredient
        
        Args:
            ingredient (str): Ingredient name
            
        Returns:
            dict: Information about the ingredient
        """
        # Check if ingredient is in our database
        score = 0
        for known_ingredient, known_score in self.ingredient_scores.items():
            if known_ingredient in ingredient or ingredient in known_ingredient:
                score = known_score
                break
        
        # Determine health impact
        if score > 5:
            health_impact = "有益健康"
            description = "这是一种对健康有益的成分"
        elif score > 0:
            health_impact = "轻微有益"
            description = "这种成分对健康有轻微益处"
        elif score == 0:
            health_impact = "中性"
            description = "这种成分对健康影响中性"
        elif score > -5:
            health_impact = "轻微不良"
            description = "这种成分对健康有轻微不良影响"
        else:
            health_impact = "不健康"
            description = "这种成分对健康有不良影响"
        
        # Check if it's a concerning additive
        is_concerning = any(additive in ingredient for additive in self.concerning_additives)
        if is_concerning:
            health_impact = "有争议"
            description = "这是一种有争议的食品添加剂，可能有潜在健康风险"
        
        return {
            "ingredient": ingredient,
            "health_impact": health_impact,
            "description": description,
            "score": score,
            "is_concerning": is_concerning
        }
    
    def _analyze_ingredient_distribution(self, total_ingredients, sugar_count, unhealthy_fat_count, 
                                       artificial_additive_count, whole_food_count, healthy_ingredient_count,
                                       preservative_count):
        """
        Analyze the distribution of ingredient types and apply scoring rules
        
        Returns:
            dict: Score adjustments, health points and scientific reasoning
        """
        score_adjustment = 0
        health_points = []
        scientific_reasoning = []
        
        # Calculate percentages
        if total_ingredients > 0:
            sugar_percentage = (sugar_count / total_ingredients) * 100
            unhealthy_fat_percentage = (unhealthy_fat_count / total_ingredients) * 100
            artificial_percentage = (artificial_additive_count / total_ingredients) * 100
            whole_food_percentage = (whole_food_count / total_ingredients) * 100
            healthy_percentage = (healthy_ingredient_count / total_ingredients) * 100
            preservative_percentage = (preservative_count / total_ingredients) * 100
            
            # Rule 1: High sugar content
            if sugar_percentage > 15:
                score_adjustment -= 15
                health_points.append("High proportion of sugar ingredients (-15 points)")
                scientific_reasoning.append("High sugar content is associated with increased risk of obesity, type 2 diabetes, and cardiovascular disease.")
            elif sugar_percentage > 8:
                score_adjustment -= 8
                health_points.append("Moderate proportion of sugar ingredients (-8 points)")
                scientific_reasoning.append("Moderate sugar content may contribute to blood glucose spikes and insulin resistance over time.")
            
            # Rule 2: Unhealthy fats
            if unhealthy_fat_percentage > 10:
                score_adjustment -= 15
                health_points.append("High proportion of unhealthy fats (-15 points)")
                scientific_reasoning.append("Trans fats and certain saturated fats increase LDL cholesterol and cardiovascular disease risk.")
            elif unhealthy_fat_percentage > 5:
                score_adjustment -= 8
                health_points.append("Contains some unhealthy fats (-8 points)")
                scientific_reasoning.append("Even moderate amounts of trans fats and certain saturated fats can negatively impact heart health.")
            
            # Rule 3: Artificial additives
            if artificial_percentage > 15:
                score_adjustment -= 12
                health_points.append("High proportion of artificial additives (-12 points)")
                scientific_reasoning.append("Multiple artificial additives may disrupt gut microbiome and have potential cumulative effects.")
            elif artificial_percentage > 5:
                score_adjustment -= 6
                health_points.append("Contains several artificial additives (-6 points)")
                scientific_reasoning.append("Artificial additives may cause adverse reactions in sensitive individuals.")
            
            # Rule 4: Preservatives
            if preservative_percentage > 10:
                score_adjustment -= 10
                health_points.append("High proportion of preservatives (-10 points)")
                scientific_reasoning.append("Multiple preservatives may have cumulative effects on gut health and metabolic function.")
            
            # Rule 5: Whole foods
            if whole_food_percentage > 50:
                score_adjustment += 15
                health_points.append("Primarily made from whole foods (+15 points)")
                scientific_reasoning.append("Whole foods provide a complex matrix of nutrients, fiber, and phytochemicals that support overall health.")
            elif whole_food_percentage > 25:
                score_adjustment += 8
                health_points.append("Contains a good amount of whole foods (+8 points)")
                scientific_reasoning.append("Whole food ingredients provide essential nutrients and fiber that support health.")
            
            # Rule 6: Healthy ingredients
            if healthy_percentage > 60:
                score_adjustment += 15
                health_points.append("Excellent nutritional profile (+15 points)")
                scientific_reasoning.append("High proportion of nutritious ingredients provides synergistic health benefits.")
            elif healthy_percentage > 30:
                score_adjustment += 8
                health_points.append("Good nutritional profile (+8 points)")
                scientific_reasoning.append("Moderate proportion of nutritious ingredients contributes to overall health.")
        
        return {
            "score_adjustment": score_adjustment,
            "health_points": health_points,
            "scientific_reasoning": scientific_reasoning
        }
    
    def _generate_recommendations(self, score, sugar_count, unhealthy_fat_count, 
                               artificial_additive_count, whole_food_count, additive_impacts):
        """
        Generate tailored recommendations based on the analysis
        
        Returns:
            tuple: (recommendations list, scientific reasoning list)
        """
        recommendations = []
        scientific_reasoning = []
        
        # Base recommendations on score
        if score < 30:
            recommendations.append("This product contains many concerning ingredients and additives.")
            recommendations.append("Consider looking for alternatives with fewer processed ingredients.")
            scientific_reasoning.append("Highly processed foods with multiple additives are associated with increased risk of chronic diseases.")
        elif score < 50:
            recommendations.append("This product has some concerning ingredients.")
            recommendations.append("Consume in moderation and look for healthier alternatives.")
            scientific_reasoning.append("Moderate consumption of processed foods may be acceptable within an otherwise healthy diet.")
        elif score < 70:
            recommendations.append("This product has a balanced nutritional profile.")
            recommendations.append("It contains some beneficial ingredients but also some less healthy ones.")
            scientific_reasoning.append("Foods with mixed nutritional profiles can be part of a healthy diet when consumed mindfully.")
        else:
            recommendations.append("This product has a good nutritional profile.")
            recommendations.append("It contains many beneficial ingredients and few concerning ones.")
            scientific_reasoning.append("Foods rich in whole, minimally processed ingredients support overall health and wellbeing.")
        
        # Specific recommendations based on analysis
        if sugar_count > 2:
            recommendations.append("Look for versions with less added sugar or naturally sweetened alternatives.")
            scientific_reasoning.append("Reducing added sugar intake helps maintain stable blood glucose levels and reduces risk of metabolic disorders.")
        
        if unhealthy_fat_count > 1:
            recommendations.append("Choose products with healthier fat sources like olive oil, avocado oil, or nuts.")
            scientific_reasoning.append("Replacing trans and certain saturated fats with mono and polyunsaturated fats improves cholesterol profiles and reduces cardiovascular risk.")
        
        if artificial_additive_count > 2:
            recommendations.append("Opt for products with fewer artificial additives and more natural ingredients.")
            scientific_reasoning.append("Minimizing exposure to multiple artificial additives may benefit long-term health, particularly for sensitive individuals.")
        
        if whole_food_count < 2 and score < 60:
            recommendations.append("Choose products that list whole foods as primary ingredients.")
            scientific_reasoning.append("Diets centered around whole, minimally processed foods are consistently associated with better health outcomes.")
        
        # Add specific recommendations based on additives
        if additive_impacts:
            # Extract just the additive names from the tuples
            additive_names = [impact[0] for impact in additive_impacts[:3]]
            recommendations.append(f"Consider avoiding products with additives like {', '.join(additive_names)}.")
            
            # Add scientific reasoning for top additives
            for additive, reason in additive_impacts[:3]:
                scientific_reasoning.append(f"{additive}: {reason}")
        
        return recommendations, scientific_reasoning
