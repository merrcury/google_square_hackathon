import React from "react";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  Button,
  Text,
} from "@chakra-ui/react";

function UserModal({ isOpen, onClose, userDetails }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>User Profile</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          {userDetails ? (
            <>
              <Text fontSize="lg" fontWeight="bold">
                Name: {userDetails.name}
              </Text>
              <Text>Email: {userDetails.email}</Text>
              {/* Add more user details here */}
            </>
          ) : (
            <Text>Loading user profile...</Text>
          )}
        </ModalBody>
        <ModalFooter>
          <Button colorScheme="blue" mr={3} onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}

export default UserModal;
