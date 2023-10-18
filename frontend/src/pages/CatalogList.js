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
  Button,
  Box,
  Image,
} from "@chakra-ui/react";
import { BsFillLightningChargeFill } from "react-icons/bs";
const token = localStorage.getItem("square_hackathon_access_token");

const CatalogList = () => {
  const [catalogs, setCatalogs] = useState([]);

  const [isGenerateImageLoading, setIsGenerateImageLoading] = useState(false);
  const [isGenerateImageLoadingIndex, setIsGenerateImageLoadingIndex] =
    useState(-1);

  const fetchCatalogues = async () => {
    try {
      const response = await backendAPIInstance.post(
        "/catalog/list",
        {},
        {
          headers: {
            "access-token": token,
          },
        }
      );
      setCatalogs(response.data.objects);
    } catch (error) {
      console.log("error in fetching catalogues -->", error);
    }
  };
  useEffect(() => {
    fetchCatalogues();
  }, []);

  const generateImage = async (dishName, index) => {
    setIsGenerateImageLoading(true);
    setIsGenerateImageLoadingIndex(index);
    try {
      const response = await backendAPIInstance.post(
        "/seller/catalog_image_generator",
        {
          dish_name: dishName,
        }
      );
      setIsGenerateImageLoading(false);
      setIsGenerateImageLoadingIndex(-1);
      const newCatalogs = [...catalogs];
      newCatalogs[index].image = response.data.image_url;
      setCatalogs(newCatalogs);
    } catch (error) {
      console.log("error in delete catalogue -->", error);
    }
  };
  return (
    <div>
      <Box marginBottom={"20px"}></Box>
      <TableContainer>
        <ChakraTable size="sm">
          <TableCaption>Catalogue List</TableCaption>
          <Thead>
            <Tr>
              <Th>Index</Th>
              <Th>Name</Th>
              <Th>Amount</Th>
              <Th>Currency</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {catalogs.map((item, _index) => {
              return (
                <Tr key={item.id}>
                  <Td>{_index + 1}</Td>
                  <Td>{item.item_data.name}</Td>
                  <Td>
                    {
                      item.item_data.variations[0].item_variation_data
                        .price_money.amount
                    }
                  </Td>
                  <Td>
                    {
                      item.item_data.variations[0].item_variation_data
                        .price_money.currency
                    }
                  </Td>
                  <Td>
                    {!item.image ? (
                      <Button
                        leftIcon={<BsFillLightningChargeFill />}
                        colorScheme="orange"
                        isLoading={
                          isGenerateImageLoading &&
                          _index === isGenerateImageLoadingIndex
                        }
                        s
                        loadingText="Generating image ..."
                        onClick={() =>
                          generateImage(item.item_data.name, _index)
                        }
                        size={"xs"}
                      >
                        Generate Image
                      </Button>
                    ) : (
                      <Image
                        boxSize="100px"
                        objectFit="cover"
                        src={item.image}
                        alt={item.item_data.name}
                      />
                    )}
                  </Td>
                </Tr>
              );
            })}
          </Tbody>
        </ChakraTable>
      </TableContainer>
    </div>
  );
};

export default CatalogList;
