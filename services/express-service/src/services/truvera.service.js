// // import api from "../api";
// import axios from "axios";
// const api = axios.create({
//   baseURL: process.env.TRUVERA_API || "https://api-testnet.truvera.io",
//   headers: {
//     Authorization: `Bearer ${process.env.TRUVERA_JWT}`,
//     "Content-Type": "application/json",
//     Accept: "*/*",
//   },
// });

// // Request interceptor
// api.interceptors.request.use(  
//   (config) => {
//     return config;
//   },
//   (error) => Promise.reject(error)
// );

// // Response interceptor
// api.interceptors.response.use(
//   (response) => response,
//   async (error) => {
//     if (error.response?.status === 401) {
//       localStorage.removeItem("token");
//       // window.location.href = "/login";
//     }
//     return Promise.reject(error);
//   }
// );

// export default api;

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

export const createProofTemplate = async (
  templateName,
  templateDescription
) => {
  try {
    const body= JSON.stringify({
      name:"Student Loan Verification",
      purpose:"Verify a student's eligibility for a loan program based on issued academic credentials.",
      input_descriptors:null,
      "expirationTime": {
        "amount": 1,
        "unit": "months"
      },
      "did":process.env.VERIFIER_DID,
    })
    const response = await api.post(`/proof-templates`, body)
    return await response.json()
  } catch (error) {
    console.error("Error creating proof template:", error)
    return null
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

const response = await fetch('https://api-testnet.truvera.io/proof-templates/'+"8d9d6b80-8871-4cc2-905f-0b2d3d3b58a0", {
    method: 'GET',
    headers: {
      "Authorization": "Bearer " + "eyJzY29wZXMiOlsidGVzdCIsImFsbCJdLCJzdWIiOiIxOTQ1MyIsInNlbGVjdGVkVGVhbUlkIjowLCJjcmVhdG9ySWQiOiIxOTQ1MyIsImZtdCI6MSwiaWF0IjoxNzUzMTUyMzg2LCJleHAiOjQ4MzI0NDgzODZ9.Bta9N3ReZywgDH90SRnySvXqDGLat40ecf4yCaYIXpHRUatz0AIuooIPf4wAXJh4z1aDtZxgvTMh4hgJyMWD9g",
      "Accept": "*/*"
    },
});

const data = await response.json();
console.log(data.request.input_descriptors[0].constraints.fields[0].path[0]);