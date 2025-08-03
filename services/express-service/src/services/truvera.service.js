import api from "./api.js";

export const issueVc = async ({
  student_DID,
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
      password: 'securepass',
      recipientEmail: "thangnnd22414@st.uel.edu.vn",
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
          id: process.env.HOLDER_DID,
          ...subject,
        },

        issuer: process.env.ISSUER_DID,
        issuanceDate: createdDate.toISOString(),
        expirationDate: expiredDate.toISOString(),
      },
      revocable: true,
    });

    const response = await api.post("/credentials", body);
    return response.data;
  } catch (error) {
    console.error("Error issuing VC:", error);
    return null;
  }
};

export const createProofTemplate = async (
  templateName,
  templateDescription
) => {
  try {
    const body = JSON.stringify({
      name: "Proof request",
      request: {
        name: "test request",
        purpose: "my purpose",
        input_descriptors: [
          {
            id: "Credential 1",
            name: "Student Loan Verification",
            purpose:
              "Verify a student's eligibility for a loan program based on issued academic credentials.",
            constraints: {
              fields: [
                {
                  path: ["$.credentialSchema.id"],
                  filter: {
                    const:
                      "https://schema.truvera.io/StudentLoanEligibilitySchema_2-V2-1753427555625.json",
                  },
                },
                {
                  path: ["$.credentialSubject.has_scholarship"],
                  filter: { type: "boolean", const: true },
                  optional: false,
                  predicate: "required",
                },
                {
                  path: ["$.credentialSubject.has_leadership_role"],
                  filter: { type: "boolean", const: false },
                  predicate: "required",
                },
                // {
                //   path: ["$.credentialSubject.scholarship_count"],
                //   filter: {
                //     type: "number",
                //     exclusiveMaximum: 100,
                //     exclusiveMinimum: 0,
                //   },
                //   predicate: "required",
                // },
              ],
            },
          },
        ],
      },
      expirationTime: {
        amount: 1,
        unit: "months",
      },
      did: "did:cheqd:testnet:7c331522-98fd-4794-9327-e61d945419bc",
    });
    const response = await api.post(`/proof-templates`, body).catch((err) => {
      if (err.response) {
        console.error("Server response:", err.response.data);
      } else {
        console.error("Unexpected error:", err.message);
      }
    });
    console.log(response.data);
    // return await response.json();
  } catch (error) {
    console.error("Error creating proof template:", error);
    return null;
  }
};

export const createProofRequest = async (student_id) => {
  try {
    const none = student_id + new Date().toDateString();

    const response = await api.post(
      `/proof-templates/${process.env.TRUVERA_TEMPLATE_REQUEST_ID}/request`,
      JSON.stringify({
        nonce: none,
        did: process.env.VERIFIER_DID,
      })
    );
    const result = await response.data;
    console.log(result);
    return result;
  } catch (error) {
    console.error("Error creating proof request:", error);
    return null;
  }
};

// createProofRequest("kk2414", "UEL")

export const getProofRequestById = async (proofRequestId) => {
  try {
    const response = await api.get(`/proof-requests/${proofRequestId}`);
    console.log(response.data);
    // return await response.data.json();
  } catch (error) {
    console.error(
      `Error fetching proof request with ID ${proofRequestId}:`,
      error
    );
    return null;
  }
};
