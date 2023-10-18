import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Text,
  Box,
} from "@chakra-ui/react";

function SummaryModal({ isOpen, onClose, summary, summaryData }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Ingredients Summary</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          {summaryData.map((type, index) => {
            return (
              <Box>
                <Text key={index} as="b">
                  {type.type}
                </Text>
                {type.ingredients.map((dish, _index) => {
                  return (
                    <Box marginLeft="20px">
                      <Text as="span" key={_index}>
                        {dish.name}{" "}
                      </Text>
                      <Text as="span" key={_index}>
                        {dish.quantity}
                      </Text>
                    </Box>
                  );
                })}
              </Box>
            );
          })}
        </ModalBody>
      </ModalContent>
    </Modal>
  );
}

export default SummaryModal;
