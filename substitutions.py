# Smart Ingredient Substitutions Database
# Making cooking accessible when you don't have everything!

INGREDIENT_SUBSTITUTIONS = {
    # Dairy Substitutions
    "heavy cream": [
        {"substitute": "milk + butter", "ratio": "3/4 cup milk + 1/4 cup melted butter", "notes": "Perfect for cooking, slightly less rich"},
        {"substitute": "evaporated milk", "ratio": "1:1 ratio", "notes": "Great for soups and sauces"},
        {"substitute": "coconut cream", "ratio": "1:1 ratio", "notes": "Adds coconut flavor, dairy-free option"}
    ],
    "buttermilk": [
        {"substitute": "milk + vinegar", "ratio": "1 cup milk + 1 tbsp white vinegar", "notes": "Let sit 5 minutes, works perfectly for baking"},
        {"substitute": "milk + lemon juice", "ratio": "1 cup milk + 1 tbsp lemon juice", "notes": "Let sit 5 minutes, slightly tangier than vinegar"},
        {"substitute": "yogurt + milk", "ratio": "1/2 cup yogurt + 1/2 cup milk", "notes": "Creates perfect consistency for pancakes"}
    ],
    "sour cream": [
        {"substitute": "greek yogurt", "ratio": "1:1 ratio", "notes": "Healthier option, same tangy flavor"},
        {"substitute": "cream cheese + milk", "ratio": "3/4 cup cream cheese + 1/4 cup milk", "notes": "Mix until smooth, richer flavor"},
        {"substitute": "cottage cheese + lemon", "ratio": "1 cup cottage cheese + 1 tsp lemon juice", "notes": "Blend smooth, lighter option"}
    ],
    
    # Egg Substitutions
    "eggs": [
        {"substitute": "applesauce", "ratio": "1/4 cup per egg", "notes": "Best for moist baked goods, adds slight sweetness"},
        {"substitute": "banana", "ratio": "1/2 mashed banana per egg", "notes": "Adds banana flavor, great for muffins and pancakes"},
        {"substitute": "flax egg", "ratio": "1 tbsp ground flaxseed + 3 tbsp water per egg", "notes": "Let sit 5 minutes, vegan option"}
    ],
    
    # Flour Substitutions
    "all-purpose flour": [
        {"substitute": "cake flour", "ratio": "1 cup + 2 tbsp cake flour per 1 cup AP flour", "notes": "Creates more tender baked goods"},
        {"substitute": "bread flour", "ratio": "Use 2 tbsp less per cup", "notes": "Creates chewier texture, great for pizza dough"},
        {"substitute": "almond flour", "ratio": "Use 1/4 less", "notes": "Gluten-free, adds nuttiness, denser texture"}
    ],
    
    # Sugar Substitutions
    "white sugar": [
        {"substitute": "brown sugar", "ratio": "1:1 ratio", "notes": "Adds molasses flavor and moisture"},
        {"substitute": "honey", "ratio": "3/4 cup per 1 cup sugar", "notes": "Reduce liquid by 1/4 cup, adds floral notes"},
        {"substitute": "maple syrup", "ratio": "3/4 cup per 1 cup sugar", "notes": "Reduce liquid by 3 tbsp, distinct maple flavor"}
    ],
    
    # Spice & Herb Substitutions
    "fresh herbs": [
        {"substitute": "dried herbs", "ratio": "1/3 the amount", "notes": "1 tbsp fresh = 1 tsp dried, add later in cooking"},
        {"substitute": "herb paste", "ratio": "1 tsp paste = 1 tbsp fresh", "notes": "More concentrated flavor"}
    ],
    "garlic": [
        {"substitute": "garlic powder", "ratio": "1/8 tsp per clove", "notes": "Less pungent, dissolves easily"},
        {"substitute": "garlic salt", "ratio": "1/2 tsp per clove", "notes": "Reduce other salt in recipe"},
        {"substitute": "shallots", "ratio": "1 small shallot per 2 cloves", "notes": "Milder, slightly sweet flavor"}
    ],
    
    # Protein Substitutions
    "ground beef": [
        {"substitute": "ground turkey", "ratio": "1:1 ratio", "notes": "Leaner option, may need extra oil for cooking"},
        {"substitute": "lentils", "ratio": "1 cup cooked lentils per 1/2 lb meat", "notes": "Vegetarian option, add extra seasoning"},
        {"substitute": "mushrooms", "ratio": "2 cups diced mushrooms per 1/2 lb meat", "notes": "Umami-rich, great texture for sauces"}
    ],
    
    # Sauce & Condiment Substitutions
    "worcestershire sauce": [
        {"substitute": "soy sauce + vinegar", "ratio": "1 tbsp soy sauce + 1/2 tsp vinegar", "notes": "Add pinch of sugar for complexity"},
        {"substitute": "fish sauce", "ratio": "Use half the amount", "notes": "More intense umami flavor"}
    ],
    "wine": [
        {"substitute": "chicken/beef broth", "ratio": "1:1 ratio", "notes": "Use broth that matches your dish"},
        {"substitute": "grape juice + vinegar", "ratio": "1 cup juice + 1 tbsp vinegar", "notes": "For white wine in cooking"}
    ]
}

def find_substitutions(ingredient):
    """Find substitutions for a given ingredient"""
    ingredient_lower = ingredient.lower().strip()
    
    # Direct match
    if ingredient_lower in INGREDIENT_SUBSTITUTIONS:
        return INGREDIENT_SUBSTITUTIONS[ingredient_lower]
    
    # Partial matches
    for key in INGREDIENT_SUBSTITUTIONS:
        if key in ingredient_lower or ingredient_lower in key:
            return INGREDIENT_SUBSTITUTIONS[key]
    
    return None

def get_substitution_suggestions(ingredients_list):
    """Get substitution suggestions for a list of ingredients"""
    suggestions = {}
    
    for ingredient in ingredients_list:
        subs = find_substitutions(ingredient)
        if subs:
            suggestions[ingredient] = subs
    
    return suggestions

# Common ingredient categories for smart suggestions
INGREDIENT_CATEGORIES = {
    "dairy": ["milk", "cream", "butter", "cheese", "yogurt", "sour cream"],
    "proteins": ["chicken", "beef", "pork", "fish", "eggs", "tofu"],
    "grains": ["flour", "rice", "pasta", "bread", "oats"],
    "sweeteners": ["sugar", "honey", "syrup", "molasses"],
    "vegetables": ["onion", "garlic", "tomato", "pepper", "carrot"],
    "herbs_spices": ["basil", "oregano", "thyme", "cumin", "paprika"]
}

def get_category_substitutions(category):
    """Get all substitutions within a category"""
    if category not in INGREDIENT_CATEGORIES:
        return {}
    
    category_subs = {}
    for ingredient in INGREDIENT_CATEGORIES[category]:
        subs = find_substitutions(ingredient)
        if subs:
            category_subs[ingredient] = subs
    
    return category_subs
