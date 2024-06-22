from pydantic import BaseModel

class Get_recommendation_response(BaseModel):
    title: str
    category: str
    link: str
    distance: str
    address: str

    def __init__(self, **data):
        super().__init__(**data)
        self.category = self.get_category(data['category'])

    def get_category(self, category):
        converted_category = category.split(" > ")
        if len(converted_category) >= 2:
            return f"{converted_category[0]} > {converted_category[1]}"
        else:
            return category
