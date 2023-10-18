import { useState } from "react";
import { Box, Button, Input, Select, VStack, useToast } from "@chakra-ui/react";
import { backendAPIInstance } from "../constants/axios";

function IngredientForm() {
  const toast = useToast();
  const [ingredient, setIngredient] = useState({
    ingredient_name: "",
    ingredient_type: "",
    shelf_life_days: "",
    quantity: "",
    unit: "",
    unitprice: "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setIngredient({
      ...ingredient,
      [name]: value,
    });
  };

  const handleAdd = async () => {
    try {
      const data = new URLSearchParams();
      data.append("ingredient_name", ingredient.ingredient_name);
      data.append("ingredient_type", ingredient.ingredient_type);
      data.append("ingredient_sub_type", ingredient.ingredient_type);
      data.append("shelf_life_days", ingredient.shelf_life_days);
      data.append("quantity", ingredient.quantity);
      data.append("unit", ingredient.unit);
      data.append("unitprice", ingredient.unitprice);

      await backendAPIInstance.post("/seller/add_ingedients", data);

      toast({
        title: "Ingredient Added",
        description: "Ingredient Added Successfully.",
        status: "success",
        duration: 2000,
        isClosable: true,
        position: "top-center",
      });
    } catch (error) {
      console.error("API Error:", error);
    }
  };

  const ingredientTypes = [
    "Dairy",
    "Nuts",
    "Spices",
    "Fruits",
    "Vegetables",
    "Flour",
    "Condiments",
    "Oil and Dressing",
    "Meat",
    "Chicken",
    "Soy",
    "Fish",
    "Seafood",
    "Other",
  ];

  const unitOptions = ["kg", "g", "l", "ml", "lb", "oz", "tbsp", "tsp"];

  return (
    <Box p={4}>
      <VStack spacing={4}>
        <Input
          name="ingredient_name"
          placeholder="Ingredient Name"
          value={ingredient.ingredient_name}
          onChange={handleChange}
          required
        />
        <Select
          name="ingredient_type"
          placeholder="Select Ingredient Type"
          value={ingredient.ingredient_type}
          onChange={handleChange}
          cursor={"pointer"}
          required
        >
          {ingredientTypes.map((type, index) => (
            <option key={index} value={type}>
              {type}
            </option>
          ))}
        </Select>

        <Input
          name="shelf_life_days"
          placeholder="Shelf Life (Days)"
          type="number"
          value={ingredient.shelf_life_days}
          onChange={handleChange}
          required
        />
        <Input
          name="quantity"
          placeholder="Quantity"
          type="number"
          value={ingredient.quantity}
          onChange={handleChange}
          required
        />
        <Select
          name="unit"
          placeholder="Select Unit"
          value={ingredient.unit}
          onChange={handleChange}
          required
        >
          {unitOptions.map((unit, index) => (
            <option key={index} value={unit}>
              {unit}
            </option>
          ))}
        </Select>
        <Input
          name="unitprice"
          placeholder="Unit Price"
          type="number"
          value={ingredient.unitprice}
          onChange={handleChange}
        />
        <Button colorScheme="teal" onClick={handleAdd}>
          Add Ingredient
        </Button>
      </VStack>
    </Box>
  );
}

export default IngredientForm;
