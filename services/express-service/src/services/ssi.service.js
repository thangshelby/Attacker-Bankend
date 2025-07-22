import api from "../api";

export const issueVc = async ({
  studentDid,
  recipientEmail,
  subject,
  password = "securepass",
}) => {
  const createdDate = new Date();
  const expiredDate = new Date(createdDate);
  expiredDate.setMonth(createdDate.getMonth() + 4);

  try {
    const body = JSON.stringify({
      persist: true,
      password,
      recipientEmail,
      algorithm: "ed25519", // hoặc "dockbbs" nếu cần ZKP
      distribute: true, // hoặc false nếu muốn gửi thủ công
      format: "jsonld",
      credential: {
        name: "Student Loan Eligibility Credential",
        description:
          "Credential to assess student's eligibility for financial support and loans.",
        schema: process.env.CREDENTIAL_SCHEMA,
        context: process.env.CREDENTIAL_CONTEXT,
        type: ["VerifiableCredential", "StudentLoanEligibilitySchema"],
        subject: {
          id: studentDid,
          ...subject,
        },
        issuer: process.env.ISSUER_DID,
        issuanceDate: createdDate.toISOString(),
        expirationDate: expiredDate.toISOString(),
      },
      revocable: true,
    });

    const response = await api.post(`/credentials`, body);
    return await response.json();
  } catch (error) {
    console.error("Error issuing VC:", error);
    return null;
  }
};

export const createProofRequest = async (studentId, school) => {
  try {
    const none = school + studentId + new Date().toDateString();

    const response = await api.post(
      `/proof-templates/${process.env.TRUVERA_TEMPLATE_REQUEST_ID}/requset`,
      JSON.stringify({
        nonce: none,
        did: process.env.ISSUER_DID,
      })
    );

    return await response.json();
  } catch (error) {
    console.error("Error creating proof request:", error);
    return null;
  }
};

export const getProofRequestById = async (proofRequestId) => {
  try {
    const response = await api.get(`/proof-requests/${proofRequestId}`);
    return await response.json();
  } catch (error) {
    console.error(
      `Error fetching proof request with ID ${proofRequestId}:`,
      error
    );
    return null;
  }
};
