class ProductFormatter:
    def format_product_details(self, product):
        """Format complete product details with enhanced information"""
        try:
            if not isinstance(product, dict):
                product = dict(product)

            # Clean up image URL
            image_url = product.get('RSkuImage1', 'N/A')
            if image_url != 'N/A':
                image_url = image_url.split(')')[0].strip()
                if not image_url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    image_url = image_url + '.jpg'

            # Process name fields
            name_parts = [
                product.get('RSkuName1', ''),
                product.get('RSkuName2', ''),
                product.get('RSkuName3', '')
            ]
            full_name = ' '.join(filter(None, name_parts))

            # Determine pack size
            pack_size = "1 piece"
            if product.get('RSkuName2') and "PCS PER PACK" in product['RSkuName2']:
                pack_parts = product['RSkuName2'].split()
                pack_size = f"{pack_parts[0]} pieces"

            # Format the response
            response = f"""Product Details:
SKU: {product.get('RSkuNo', 'N/A')}
Name: {full_name}
Brand: {product.get('RSkuBrnName', 'N/A')}
Category: {product.get('RSkuPrName', 'N/A')}
Pack Size: {pack_size}
Color: {product.get('RSkuInkName', 'N/A')}
Unit: {product.get('RUom', 'N/A')}
Minimum Order: {product.get('RSkuMoq', 'N/A')}
Stock Available: {product.get('RQoh', 'N/A')}
Price: ${product.get('RSkuPrice', 'N/A')}"""

            if image_url != 'N/A':
                response += f"\nImage: {image_url}"

            # Add product link if available
            if product.get('RSkulink'):
                response += f"\nProduct Link: {product.get('RSkulink')}"

            return response

        except Exception as e:
            print(f"Error formatting product details: {str(e)}")
            return "Error: Could not format product details"

    def format_product_list(self, products, products_data, detailed=False):
        """Format list of products with enhanced information"""
        if not products:
            return "No matching products found. Please try a different search."

        try:
            products_data = [dict(p) for p in products_data]
            response = "Here are the matching products:\n\n"

            if not detailed:
                for idx, product in enumerate(products, 1):
                    full_product = next((p for p in products_data if p['RSkuNo'] == product['sku']), None)
                    if full_product:
                        name_parts = [
                            full_product.get('RSkuName1', ''),
                            full_product.get('RSkuName2', '')
                        ]
                        display_name = ' '.join(filter(None, name_parts))
                        response += f"{idx}. {full_product.get('RSkuBrnName', 'N/A')} - {display_name}\n"
                        response += f"   SKU: {full_product.get('RSkuNo', 'N/A')}\n"
                        response += f"   Color: {full_product.get('RSkuInkName', 'N/A')}\n"
                        if full_product.get('RSkulink'):
                            response += f"   Product Link: {full_product.get('RSkulink')}\n"
                        response += "\n"

                response += "\nTo see full details for any product, please ask for product details with the SKU number."
                return response

            for idx, product in enumerate(products, 1):
                full_product = next((p for p in products_data if p['RSkuNo'] == product['sku']), None)
                if full_product:
                    response += f"{idx}. {self.format_product_details(full_product)}\n\n"

            return response

        except Exception as e:
            print(f"Error formatting product list: {str(e)}")
            return "Error: Could not format product list"