class BasicSearcher:
    def basic_product_search(self, description, product_names):
        description = description.lower()
        search_terms = description.split()
        matches = []

        for product in product_names:
            score = 0
            searchable_text = (
                f"{product['brand']} {product['name']} {product['name1']} "
                f"{product['name2']} {product['name3']} {product['category']}"
            ).lower()

            # Give points for any term match anywhere in the text
            for term in search_terms:
                if term in searchable_text:
                    score += 1

                # Extra points for brand/name matches
                if term in product['brand'].lower():
                    score += 2
                if term in product['name'].lower():
                    score += 2

            if score > 0:
                matches.append({
                    'score': score,
                    'sku': product['sku'],
                    'brand': product['brand'],
                    'name': product['name'],
                    'category': product['category'],
                    'color': product['color']
                })

        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:5] if matches else []