#!/usr/bin/env python3
"""
Production Hungie API Server
Optimized for deployment on Railway/Heroku
"""

import os
import sqlite3
import json
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from substitutions import find_substitutions, get_substitution_suggestions, INGREDIENT_SUBSTITUTIONS

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
PORT = int(os.getenv("PORT", 8000))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "hungie.db")

# Create FastAPI app
app = FastAPI(
    title="Hungie API", 
    version="1.0.0",
    description="The anti-SEO recipe platform with AI-powered substitutions",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None
)

# CORS configuration for production
if ENVIRONMENT == "production":
    # Production CORS - restrict to your domain
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://hungie.vercel.app",
            "https://hungie.app", 
            "https://*.hungie.app"
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
else:
    # Development CORS - allow all
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize OpenAI client
client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI client initialized")
else:
    print("⚠️  OpenAI API key not found - AI features disabled")

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "ai_enabled": client is not None,
        "database": "connected" if Path(DATABASE_URL).exists() else "missing"
    }

# Root endpoint
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Hungie API! 🍴",
        "version": "1.0.0", 
        "features": [
            "92+ curated recipes",
            "AI-powered chat with substitutions",  
            "Smart ingredient replacements",
            "Anti-SEO design philosophy"
        ],
        "docs": "/docs" if ENVIRONMENT == "development" else "disabled_in_production"
    }

# Database connection with error handling
def get_db():
    """Get database connection with proper error handling"""
    try:
        if not Path(DATABASE_URL).exists():
            raise FileNotFoundError(f"Database not found: {DATABASE_URL}")
        
        conn = sqlite3.connect(DATABASE_URL)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Import existing models and endpoints from server.py
class ChatRequest(BaseModel):
    message: str
    context: str = ""

class SubstitutionRequest(BaseModel):
    ingredient: str
    recipe_context: str = ""

class BulkSubstitutionRequest(BaseModel):
    ingredients: List[str]
    recipe_context: str = ""

@app.middleware("http")
async def log_requests(request, call_next):
    """Log API requests for analytics"""
    response = await call_next(request)
    
    # Log to console (will be captured by deployment platform)
    print(f"API: {request.method} {request.url.path} - {response.status_code}")
    
    return response

# Import all endpoints from main server
@app.get("/api/recipes")
def get_recipes(page: int = 1, limit: int = 20):
    """Get paginated list of all recipes"""
    try:
        offset = (page - 1) * limit
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT r.id, r.name, r.description, r.total_time, r.servings
            FROM recipes r
            INNER JOIN instructions i ON r.id = i.recipe_id
            INNER JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            ORDER BY r.name
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        recipes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "success": True,
            "data": recipes,
            "total": len(recipes),
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recipes/{recipe_id}")
def get_recipe(recipe_id: str):
    """Get single recipe with full details"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get recipe basic info
        cursor.execute("""
            SELECT id, name, description, total_time, servings
            FROM recipes 
            WHERE id = ?
        """, (recipe_id,))
        
        recipe_row = cursor.fetchone()
        if not recipe_row:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        recipe = dict(recipe_row)
        
        # Get ingredients
        cursor.execute("""
            SELECT i.name, ri.amount, ri.unit
            FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE ri.recipe_id = ?
            ORDER BY i.name
        """, (recipe_id,))
        
        recipe['ingredients'] = [dict(row) for row in cursor.fetchall()]
        
        # Get instructions
        cursor.execute("""
            SELECT step_number, instruction
            FROM instructions
            WHERE recipe_id = ?
            ORDER BY step_number
        """, (recipe_id,))
        
        recipe['instructions'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return {"success": True, "data": recipe}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
def search_recipes(q: str):
    """Search recipes by name, description, or ingredients"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        search_pattern = f"%{q}%"
        
        cursor.execute("""
            SELECT DISTINCT r.id, r.name, r.description, r.total_time, r.servings
            FROM recipes r
            INNER JOIN instructions inst ON r.id = inst.recipe_id
            INNER JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            LEFT JOIN ingredients i ON ri.ingredient_id = i.id
            WHERE r.name LIKE ? OR r.description LIKE ? OR i.name LIKE ?
            ORDER BY r.name
            LIMIT 50
        """, (search_pattern, search_pattern, search_pattern))
        
        recipes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return {
            "success": True,
            "data": recipes,
            "query": q,
            "total": len(recipes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
def get_categories():
    """Get all recipe categories with counts"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.name, COUNT(DISTINCT r.id) as count
            FROM categories c
            INNER JOIN recipe_categories rc ON c.id = rc.category_id
            INNER JOIN recipes r ON rc.recipe_id = r.id
            INNER JOIN instructions i ON r.id = i.recipe_id
            INNER JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            GROUP BY c.id, c.name
            ORDER BY count DESC, c.name
        """)
        
        categories = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]
        conn.close()
        
        return {"success": True, "data": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_hungie_personality_prompt():
    """Get the core Hungie AI personality prompt"""
    return """You are Hungie, an enthusiastic and encouraging chef AI assistant with a unique personality. Your mission is to help people discover and cook amazing food.

PERSONALITY TRAITS:
- Encouraging and supportive (never intimidating)
- Passionate about food and cooking
- Practical and direct (no fluff, just helpful advice)
- Fun and energetic (use emojis and excitement)
- Uses "Yes, Chef!" as a signature catchphrase when appropriate
- Speaks like a knowledgeable but friendly chef who wants everyone to succeed

ANTI-SEO PHILOSOPHY:
- No long backstories or filler content
- Get straight to the point
- Focus on practical cooking help
- Make food accessible, not intimidating

CORE VALUES:
- Real food for real people
- Everyone can cook with confidence
- Substitutions and creativity are encouraged
- Cooking should be fun, not stressful"""

@app.post("/api/chat")
def chat_with_hungie(request: ChatRequest):
    """Chat with Hungie AI for personalized recipe recommendations"""
    try:
        if not client:
            return {
                "success": False,
                "error": "AI features not available",
                "response": "Yes, Chef! I'm having some technical difficulties right now, but I'm still here to help! Try searching our recipes directly, or ask me later!"
            }
            
        # Get recipe data for context
        conn = get_db()
        cursor = conn.cursor()
        
        # Get a sample of available recipes for context
        cursor.execute("""
            SELECT DISTINCT r.name, r.description, r.total_time, r.servings
            FROM recipes r
            INNER JOIN instructions i ON r.id = i.recipe_id
            INNER JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            ORDER BY r.name
            LIMIT 20
        """)
        
        sample_recipes = [dict(row) for row in cursor.fetchall()]
        
        # Get category information
        cursor.execute("""
            SELECT c.name, COUNT(DISTINCT r.id) as recipe_count
            FROM categories c
            INNER JOIN recipe_categories rc ON c.id = rc.category_id
            INNER JOIN recipes r ON rc.recipe_id = r.id
            INNER JOIN instructions i ON r.id = i.recipe_id
            INNER JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            GROUP BY c.id, c.name
            ORDER BY recipe_count DESC
            LIMIT 10
        """)
        
        categories = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]
        conn.close()
        
        # Build context for AI
        recipe_context = f"""
AVAILABLE RECIPES SAMPLE: {json.dumps(sample_recipes[:10], indent=2)}

POPULAR CATEGORIES: {json.dumps(categories, indent=2)}

TOTAL DATABASE: 92+ complete recipes with full ingredients and instructions
        """
        
        # Create AI prompt with better context handling
        system_prompt = get_hungie_personality_prompt()
        user_message = f"""
Context about our recipe database:
{recipe_context}

Previous conversation context: {request.context}

User's message: {request.message}

Please respond as Hungie, keeping in mind:
1. We have 92+ complete recipes in our database
2. Focus on being helpful and encouraging
3. If they're looking for specific recipes, mention we can search our database
4. Use "Yes, Chef!" when appropriate
5. Ask follow-up questions to better understand their needs
6. Keep it conversational and fun!
        """
        
        # Get AI response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        return {
            "success": True,
            "response": ai_response,
            "suggestions": []  # We can add recipe suggestions later
        }
        
    except Exception as e:
        # Fallback response if AI fails
        fallback_responses = [
            "Yes, Chef! 🍴 I'm here to help you find something delicious! What are you craving today?",
            "Right then! Let's get you sorted with some amazing food. What's the situation - quick meal, comfort food, or trying something new?",
            "Brilliant! I love helping people discover great recipes. Tell me more about what you're looking for and I'll find you something perfect!",
        ]
        
        return {
            "success": True,
            "response": fallback_responses[0],
            "suggestions": [],
            "fallback": True
        }

@app.post("/api/smart-search")
def smart_search(request: ChatRequest):
    """AI-powered search that combines chat response with recipe results"""
    try:
        message_lower = request.message.lower()
        
        # Check if this is a substitution question
        substitution_keywords = [
            'substitute', 'replace', 'instead of', 'don\'t have', 'out of', 
            'alternative', 'swap', 'use instead', 'without', 'missing'
        ]
        
        is_substitution_query = any(keyword in message_lower for keyword in substitution_keywords)
        
        # If it's a substitution query, handle it specially
        if is_substitution_query:
            # Try to extract the ingredient they need a substitute for
            potential_ingredients = []
            for ingredient in INGREDIENT_SUBSTITUTIONS.keys():
                if ingredient in message_lower:
                    potential_ingredients.append(ingredient)
            
            if potential_ingredients:
                # Get substitutions for the first matched ingredient
                ingredient = potential_ingredients[0]
                substitutions = find_substitutions(ingredient)
                
                # Create AI response with substitution advice
                if client:
                    sub_prompt = f"""
                    The user is asking about substitutions for {ingredient}. 
                    
                    Available substitutions: {json.dumps(substitutions, indent=2)}
                    
                    User's original question: {request.message}
                    
                    As Hungie, provide encouraging advice about these substitutions. Start with "Yes, Chef!" 
                    and give practical guidance about which substitute would work best.
                    """
                    
                    try:
                        ai_response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": get_hungie_personality_prompt()},
                                {"role": "user", "content": sub_prompt}
                            ],
                            max_tokens=250,
                            temperature=0.7
                        )
                        chat_response = ai_response.choices[0].message.content.strip()
                    except Exception:
                        chat_response = f"Yes, Chef! I've got some great substitutes for {ingredient}. Let me help you out!"
                else:
                    chat_response = f"Yes, Chef! I've got some great substitutes for {ingredient}. Let me help you out!"
                
                return {
                    "success": True,
                    "chat_response": chat_response,
                    "recipes": [],
                    "search_terms": [ingredient],
                    "substitutions": {ingredient: substitutions},
                    "type": "substitution_response"
                }
        
        # Regular recipe search logic continues below...
        # First, try to extract search terms and find recipes
        search_terms = []
        
        # Look for food-related keywords (expanded list)
        food_keywords = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'pizza', 'burger',
            'salad', 'soup', 'dessert', 'cake', 'cookies', 'bread', 'rice', 'noodles',
            'vegetables', 'healthy', 'quick', 'easy', 'cheap', 'budget', 'kids',
            'spicy', 'hot', 'mild', 'sweet', 'sour', 'chinese', 'italian', 'mexican',
            'indian', 'thai', 'breakfast', 'lunch', 'dinner', 'snack', 'appetizer',
            'main', 'side', 'comfort', 'fried', 'grilled', 'baked', 'steamed'
        ]
        
        for keyword in food_keywords:
            if keyword in message_lower:
                search_terms.append(keyword)
        
        # Also look for common food words that might not be in our list
        words = message_lower.split()
        potential_terms = [word for word in words if len(word) > 3 and word not in ['what', 'want', 'need', 'like', 'have', 'make', 'cook', 'something', 'anything']]
        search_terms.extend(potential_terms)
        
        # Remove duplicates
        search_terms = list(set(search_terms))
        
        # Get recipe results if we have search terms
        recipes = []
        if search_terms:
            conn = get_db()
            cursor = conn.cursor()
            
            # Build dynamic search query for multiple terms
            search_conditions = []
            search_params = []
            
            for term in search_terms[:3]:  # Use up to 3 terms
                search_pattern = f"%{term}%"
                search_conditions.extend([
                    "r.name LIKE ?",
                    "r.description LIKE ?", 
                    "i.name LIKE ?"
                ])
                search_params.extend([search_pattern, search_pattern, search_pattern])
            
            if search_conditions:
                query = f"""
                    SELECT DISTINCT r.id, r.name, r.description, r.total_time, r.servings
                    FROM recipes r
                    INNER JOIN instructions inst ON r.id = inst.recipe_id
                    INNER JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                    LEFT JOIN ingredients i ON ri.ingredient_id = i.id
                    WHERE ({' OR '.join(search_conditions)})
                    ORDER BY r.name
                    LIMIT 6
                """
                
                cursor.execute(query, search_params)
                recipes = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
        
        # Now get AI response, informed by what we found
        context_message = request.message
        if recipes:
            context_message += f"\n\nFound {len(recipes)} matching recipes. Please provide encouraging response and mention some of these options."
        
        if client:
            chat_request_with_context = ChatRequest(message=context_message)
            chat_response_data = chat_with_hungie(chat_request_with_context)
            chat_response = chat_response_data["response"]
        else:
            chat_response = "Yes, Chef! 🍴 I'm here to help you find something delicious! What are you craving today?"
        
        return {
            "success": True,
            "chat_response": chat_response,
            "recipes": recipes,
            "search_terms": search_terms
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/substitutions")
def get_ingredient_substitution(request: SubstitutionRequest):
    """Get substitutions for a single ingredient with AI enhancement"""
    try:
        # Get basic substitutions from our database
        substitutions = find_substitutions(request.ingredient)
        
        if not substitutions:
            return {
                "success": False,
                "message": f"No substitutions found for '{request.ingredient}'",
                "ingredient": request.ingredient,
                "substitutions": []
            }
        
        # Enhance with AI context if recipe context is provided
        ai_advice = ""
        if request.recipe_context and client:
            ai_prompt = f"""
            The user is making {request.recipe_context} and needs a substitute for {request.ingredient}.
            
            Available substitutions: {json.dumps(substitutions, indent=2)}
            
            As Hungie, provide ONE brief, encouraging recommendation for the best substitute given this recipe context. 
            Start with "Yes, Chef!" and be practical and supportive.
            """
            
            try:
                ai_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": get_hungie_personality_prompt()},
                        {"role": "user", "content": ai_prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                ai_advice = ai_response.choices[0].message.content.strip()
            except Exception as e:
                ai_advice = f"Yes, Chef! I'd recommend trying one of these substitutes - they'll work great in your dish!"
        
        return {
            "success": True,
            "ingredient": request.ingredient,
            "substitutions": substitutions,
            "ai_advice": ai_advice,
            "recipe_context": request.recipe_context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/substitutions/bulk")
def get_bulk_substitutions(request: BulkSubstitutionRequest):
    """Get substitutions for multiple ingredients"""
    try:
        results = {}
        
        for ingredient in request.ingredients:
            substitutions = find_substitutions(ingredient)
            if substitutions:
                results[ingredient] = substitutions
        
        # Get AI overview if recipe context provided
        ai_overview = ""
        if request.recipe_context and results and client:
            ai_prompt = f"""
            The user is making {request.recipe_context} and needs substitutes for these ingredients: {', '.join(request.ingredients)}.
            
            Found substitutions for: {', '.join(results.keys())}
            
            As Hungie, provide a brief, encouraging overview with your top recommendations. 
            Start with "Yes, Chef!" and prioritize the most important substitutions.
            """
            
            try:
                ai_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": get_hungie_personality_prompt()},
                        {"role": "user", "content": ai_prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                ai_overview = ai_response.choices[0].message.content.strip()
            except Exception as e:
                ai_overview = "Yes, Chef! I found some great substitution options for you!"
        
        return {
            "success": True,
            "requested_ingredients": request.ingredients,
            "substitutions": results,
            "missing_ingredients": [ing for ing in request.ingredients if ing not in results],
            "ai_overview": ai_overview,
            "recipe_context": request.recipe_context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/substitutions/browse")
def browse_substitutions():
    """Browse all available substitutions by category"""
    try:
        return {
            "success": True,
            "total_ingredients": len(INGREDIENT_SUBSTITUTIONS),
            "substitutions": INGREDIENT_SUBSTITUTIONS,
            "message": "Browse our complete substitution database!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple health endpoint for deployment monitoring
@app.get("/healthcheck")
def healthcheck():
    """Simple health check endpoint that always works"""
    return {"status": "ok", "message": "Hungie API is healthy!"}

if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting Hungie API in {ENVIRONMENT} mode...")
    print(f"📊 Database: {DATABASE_URL}")
    print(f"🤖 AI Features: {'Enabled' if client else 'Disabled'}")
    
    uvicorn.run(
        "prod_server:app",
        host="0.0.0.0", 
        port=PORT,
        reload=ENVIRONMENT == "development"
    )
