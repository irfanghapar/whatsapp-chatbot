class ProductFinder:
    def __init__(self, client=None):
        self.client = client

    def find_product_by_sku(self, products_data, sku):
        """Find product by SKU number"""
        return next((p for p in products_data if p['RSkuNo'] == sku), None)

    def find_matching_products(self, description, products_data, product_names, basic_searcher):
        """Find products matching the description using AI"""
        try:
            if not self.client:
                return basic_searcher.basic_product_search(description, product_names)

            # Format product data for AI in a more structured way
            products_json = []
            for p in product_names:
                products_json.append({
                    "sku": p['sku'],
                    "brand": p['brand'],
                    "name": p['name'],
                    "category": p['category'],
                    "color": p['color'],
                    "specifications": p['name2'] if p['name2'] else "",
                    "additional_info": p['name3'] if p['name3'] else ""
                })

            system_prompt = """You are a product search expert. Analyze the following product catalog and find matches:

            Product Catalog:
            {}

            Instructions:
            1. Analyze the user's search query
            2. Find products that best match the query considering brand names, descriptions, specifications, and categories
            3. Return only the SKU numbers of matching products, separated by commas
            4. If no matches found, return "NO_MATCH"

            Example Response Format:
            SKU123,SKU456,SKU789"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-16k", # Using 16k model for larger context
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt.format(str(products_json[:1000])) # Limiting to first 1000 products
                    },
                    {
                        "role": "user",
                        "content": f"Find products matching this description: {description}"
                    }
                ],
                temperature=0.3,
            )

            sku_list = response.choices[0].message.content.strip()

            if sku_list == "NO_MATCH":
                return basic_searcher.basic_product_search(description, product_names)

            matching_products = []
            for sku in sku_list.split(','):
                sku = sku.strip()
                product = next((p for p in product_names if p['sku'] == sku), None)
                if product:
                    matching_products.append({
                        'sku': product['sku'],
                        'brand': product['brand'],
                        'name': product['name'],
                        'category': product['category'],
                        'color': product['color']
                    })

            return matching_products[:5] if matching_products else basic_searcher.basic_product_search(description, product_names)

        except Exception as e:
            print(f"Error in AI product matching: {str(e)}")
            return basic_searcher.basic_product_search(description, product_names)