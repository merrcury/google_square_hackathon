import React, { useEffect, useState } from "react";
import { backendAPIInstance } from "../constants/axios";
import {
  Table as ChakraTable,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableCaption,
  TableContainer,
  IconButton,
  Button,
  useDisclosure,
  Box,
} from "@chakra-ui/react";
import { AiFillDelete, AiFillPlusCircle } from "react-icons/ai";
import { BsFillLightningChargeFill } from "react-icons/bs";
import { useNavigate } from "react-router-dom";
import SummaryModal from "../components/SummaryModal";

const IngredientsList = () => {
  const navigate = useNavigate();
  const [ingredients, setIngredients] = useState([]);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [summaryData, setSummaryData] = useState([]);
  const [isSummaryLoading, setIsSummaryLoading] = useState(false);

  const fetchIngredients = async () => {
    try {
      const response = await backendAPIInstance.post("/ingredients/read");
      setIngredients(JSON.parse(response.data));
    } catch (error) {
      console.log("error in fetching ingredients -->", error);
    }
  };
  useEffect(() => {
    fetchIngredients();
  }, []);

  const deleteIngredient = async (name) => {
    try {
      await backendAPIInstance.post("/ingredients/delete", {
        name: name,
      });
    } catch (error) {
      console.log("error in delete ingredient -->", error);
    }
  };

  const summarizeIngredients = async () => {
    setIsSummaryLoading(true);
    try {
      const response = await backendAPIInstance.post(
        "/seller/get_ingredient_summary"
      );

      const arr = [];
      for (const [key, value] of Object.entries(response.data)) {
        arr.push({ type: key, ingredients: value });
      }
      setIsSummaryLoading(false);
      setSummaryData(arr);
      onOpen();
    } catch (error) {
      console.log("error -->", error);
      setIsSummaryLoading(false);
      onOpen();
    }
  };

  return (
    <div>
      <Box marginBottom={"20px"}>
        <Button
          leftIcon={<AiFillPlusCircle />}
          colorScheme="green"
          onClick={() => navigate("/add-ingredients")}
          marginRight={"20px"}
        >
          Add Ingredient
        </Button>
        <Button
          leftIcon={<BsFillLightningChargeFill />}
          colorScheme="orange"
          isLoading={isSummaryLoading}
          loadingText="Generating Summary ..."
          onClick={() => summarizeIngredients()}
          marginRight={"20px"}
        >
          Summarize Ingredients
        </Button>
      </Box>
      <TableContainer>
        <ChakraTable size="sm">
          <TableCaption>Ingredients List</TableCaption>
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Type</Th>
              <Th>Sub Type</Th>
              <Th>Shelf Life (In days)</Th>
              <Th>Quantity</Th>
              <Th>Unit</Th>
              <Th>Unit Price</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {ingredients.map((item) => {
              return (
                <Tr key={item.ingredient_id}>
                  <Td>{item.name}</Td>
                  <Td>{item.ingredient_type}</Td>
                  <Td>{item.ingredient_sub_type}</Td>
                  <Td>{item.shelf_life_days}</Td>
                  <Td>{item.quantity}</Td>
                  <Td>{item.unit}</Td>
                  <Td>{item.unitprice} CAD</Td>
                  <Td>
                    <IconButton
                      aria-label="Search database"
                      icon={<AiFillDelete />}
                      onClick={() => deleteIngredient(item.name)}
                    />
                  </Td>
                </Tr>
              );
            })}
          </Tbody>
        </ChakraTable>
      </TableContainer>
      <SummaryModal
        isOpen={isOpen}
        onClose={onClose}
        summaryData={summaryData}
      />
    </div>
  );
};

export default IngredientsList;
