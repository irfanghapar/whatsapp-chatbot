class QueryAnalyzer:
    def __init__(self, client):
        self.client = client

    def analyze_query(self, query):
        """Analyze user query to determine if it contains SKU or product description"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the query and extract either:
                        1. SKU number if present (exact match)
                        2. Product description if no SKU (include brand names and product types)
                        Return in format: 
                        SKU:number or PRODUCT:description
                        Example: 'I want Stabilo and Pilot pens' -> PRODUCT:stabilo pilot pen"""
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0
            )
            result = response.choices[0].message.content.strip()
            type_value = result.split(':', 1)

            if len(type_value) != 2:
                return None, None

            query_type, value = type_value
            return query_type.upper(), value.strip()

        except Exception as e:
            print(f"Error analyzing query: {str(e)}")
            return None, None