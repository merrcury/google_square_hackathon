import React, { useState } from "react";
import { backendAPIInstance } from "../constants/axios";
import { Button, Input, Box, Flex, Avatar, Text } from "@chakra-ui/react";
import { BiLogoTelegram } from "react-icons/bi";
import { BsFillCartPlusFill } from "react-icons/bs";
import MyModal from "../components/Modal";

const token = localStorage.getItem("square_hackathon_access_token");
const locationId = localStorage.getItem("square_hackathon_seller_location");

const cleanTheString = (str) => {
  return str
    .replaceAll("(", "{")
    .replaceAll(")", "}")
    .replaceAll("none", null)
    .replace("cad", "CAD");
};

function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}
const Chat = () => {
  const [history, setHistory] = useState("");
  const [message, setMessage] = useState("");
  const [chats, setChats] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [statusText, setStatusText] = useState("Generating Order Summary ...");
  const [orderSummary, setOrderSummary] = useState(null);

  const [showCustomerForm, setShowCustomerForm] = useState(false);
  const [customerId, setCustomerId] = useState(null);

  const handleModalClose = () => {
    setStatusText("Generating Order Summary ...");
    setOrderSummary("");
    setCustomerId(null);

    setShowCustomerForm(false);
    setIsModalOpen(false);
  };

  const sendMessage = async (stop) => {
    try {
      let newChats = [...chats];
      newChats.push({
        customer: stop ? "stop" : message,
        agent: "AI is thinking ...",
      });
      setChats(newChats);

      const response = await backendAPIInstance.post(
        "/customer/chat",
        { message: stop ? "stop" : message, history },
        {
          headers: {
            "access-token": token,
          },
        }
      );
      newChats[newChats.length - 1].agent = response.data.response;
      setHistory(JSON.stringify(response.data.history[1]));
      setChats(newChats);
      setMessage("");
    } catch (error) {
      console.log("error in sending message -->", error);
    }
  };

  const order = async () => {
    setIsModalOpen(true);
    const res = await backendAPIInstance.post("/customer/order_summarization", {
      history: JSON.stringify(chats),
    });

    let stringifiedData;
    let parsedData;
    //to handle the case when the response is not a valid JSON
    try {
      stringifiedData = JSON.stringify(res.data);
      stringifiedData = cleanTheString(stringifiedData);
      parsedData = JSON.parse(stringifiedData);
      parsedData = JSON.parse(parsedData);
    } catch (error) {
      console.error("Error parsing JSON:", error);
    }
    let payload = parsedData.order[0];
    payload = {
      name: payload.name,
      quantity: payload.quantity.toString(),
      base_price_money: payload.base_price_money,
    };
    setStatusText("Order Summary");
    setOrderSummary(payload);
  };

  const CustomerForm = () => {
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");

    const createCustomer = async () => {
      const customerResponse = await backendAPIInstance.post(
        "/invoice/create_customer",
        {
          first_name: firstName,
          last_name: lastName,
          email: email,
          phone_number: "5145832589",
          address_line_1: "11 - 3795",
          postal_code: "H3T 1H",
          country: "CA",
          birthday: "1992-02-19",
        },
        {
          headers: {
            "access-token": token,
          },
        }
      );

      setCustomerId(customerResponse.data.customer.id);
      setStatusText(`Saved Customer Details ..`);
      setShowCustomerForm(false);

      setStatusText("Creating Order ...");

      const response = await backendAPIInstance.post(
        "/order/create",
        {
          orders: JSON.stringify(orderSummary),
          customer_id: customerResponse.data.customer.id,
        },
        {
          headers: {
            "access-token": token,
            "location-id": locationId,
          },
        }
      );

      setStatusText("Order Placed Successfully");

      setStatusText(`Generating Invoice for ${firstName}`);
      await backendAPIInstance.post(
        "/invoice/create",
        {
          order_id: response.data.order.id,
          customer_id: customerResponse.data.customer.id,
        },
        {
          headers: {
            "access-token": token,
            "location-id": locationId,
          },
        }
      );
      setStatusText("Order invoice sent to your email");
    };

    return (
      <Box>
        <Flex marginBottom="10px">
          <Input
            marginRight="10px"
            type="text"
            placeholder="First Name"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
          <Input
            type="text"
            placeholder="Last Name"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
        </Flex>
        <Flex>
          <Input
            marginRight="10px"
            type="text"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Button colorScheme="orange" onClick={() => createCustomer()}>
            Create
          </Button>
        </Flex>
      </Box>
    );
  };

  const SummaryDetails = () => {
    return (
      <Box>
        {orderSummary && (
          <Box>
            <Box>
              <Text as="b" size="xs">
                Dish Name:{" "}
              </Text>
              <Text as="span" size="xs">
                {capitalizeFirstLetter(orderSummary.name)}
              </Text>
            </Box>
            <Box>
              <Text as="b" size="xs">
                Quantity:{" "}
              </Text>
              <Text as="span" size="xs">
                {orderSummary.quantity}
              </Text>
            </Box>
            <Box>
              <Text as="b" size="xs">
                Money:{" "}
              </Text>
              <Text as="span" size="xs">
                {orderSummary.base_price_money.amount}{" "}
                {orderSummary.base_price_money.currency}
              </Text>
            </Box>
          </Box>
        )}
      </Box>
    );
  };

  const ModalBody = () => {
    if (showCustomerForm) {
      return <CustomerForm />;
    } else {
      return <SummaryDetails />;
    }
  };

  const ModalFooter = () => {
    return (
      !showCustomerForm &&
      customerId === null && (
        <Button
          onClick={() => {
            setStatusText("Enter your details to proceed");
            setShowCustomerForm(true);
          }}
          colorScheme="teal"
        >
          Confirm and Proceed
        </Button>
      )
    );
  };

  return (
    <Box backgroundColor={"white"}>
      <Box
        height={"75vh"}
        maxHeight={"75vh"}
        // border={"2px solid red"}
        scrollBehavior={"smooth"}
        overflow={"scroll"}
        padding={"20px"}
      >
        {chats.map((chat, _i) => {
          return (
            <Box key={_i}>
              <Flex marginBottom={"20px"}>
                <Avatar
                  size="sm"
                  name="User Avatar"
                  src="https://cdn-icons-png.flaticon.com/512/6596/6596121.png"
                  marginRight={"10px"}
                />
                <Text as="span" fontSize={"md"}>
                  {chat.customer}
                </Text>
              </Flex>
              <Flex marginBottom={"20px"}>
                <Avatar
                  size="sm"
                  name="Bot Avatar"
                  src="https://static.vecteezy.com/system/resources/previews/010/054/157/original/chat-bot-robot-avatar-in-circle-round-shape-isolated-on-white-background-stock-illustration-ai-technology-futuristic-helper-communication-conversation-concept-in-flat-style-vector.jpg"
                  marginRight={"10px"}
                />
                <Text as="span"> {chat.agent}</Text>
              </Flex>
            </Box>
          );
        })}
      </Box>
      <Box height={"10vh"} padding={"10px"}>
        <Flex direction={"row"}>
          <Input
            placeholder="Enter your message"
            onChange={(e) => setMessage(e.target.value)}
            marginRight={"20px"}
            value={message}
          />
          <Button
            colorScheme="orange"
            size={"md"}
            onClick={() => sendMessage()}
            marginRight={"10px"}
            rightIcon={<BiLogoTelegram />}
          >
            Send
          </Button>
          <Button
            colorScheme="teal"
            size={"md"}
            onClick={() => {
              setMessage("stop");
              sendMessage(true);
            }}
            marginRight={"10px"}
          >
            Stop
          </Button>
          <Button
            colorScheme="green"
            size={"md"}
            onClick={() => order()}
            rightIcon={<BsFillCartPlusFill />}
          >
            Order
          </Button>
        </Flex>
      </Box>
      <MyModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        title={statusText}
        body={<ModalBody />}
        footer={<ModalFooter />}
      />
    </Box>
  );
};

export default Chat;
