// // import api from "../api";
import fs from "fs";

const jwt =
  "eyJzY29wZXMiOlsidGVzdCIsImFsbCJdLCJzdWIiOiIxOTQ1MyIsInNlbGVjdGVkVGVhbUlkIjowLCJjcmVhdG9ySWQiOiIxOTQ1MyIsImZtdCI6MSwiaWF0IjoxNzUzMTUyMzg2LCJleHAiOjQ4MzI0NDgzODZ9.Bta9N3ReZywgDH90SRnySvXqDGLat40ecf4yCaYIXpHRUatz0AIuooIPf4wAXJh4z1aDtZxgvTMh4hgJyMWD9g";
import axios from "axios";
const api = axios.create({
  baseURL: "https://api-testnet.truvera.io",
  headers: {
    Authorization: `Bearer ${jwt}`,
    "Content-Type": "application/json",
    Accept: "*/*",
  },
});

export default api;


const data = await response.json();
fs.writeFileSync('did-export.jsonld', JSON.stringify(data, null, 2), 'utf-8');
console.log(data);



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
      distribute: false, // hoặc false nếu muốn gửi thủ công
      format: "jsonld",
      credential: {
        name: "Student Loan Eligibility Credential",
        description:
          "Credential to assess student's eligibility for financial support and loans.",
        schema:
          "https://schema.truvera.io/StudentLoanEligibilitySchema_2-V2-1753427555625.json",
        context:
          "https://schema.truvera.io/StudentLoanEligibilitySchema_2-V1753427555625.json-ld",
        type: ["VerifiableCredential", "StudentLoanEligibilitySchema"],
        subject: {
          id: studentDid,
          name: "ngo nguyen duc thang",
          current_gpa: 3.7,
          has_scholarship: true,
          scholarship_count: 4,
          failed_courses_count: 0,
          has_leadership_role: false,
          academic_award_count: 10,
          total_credits_earned: 10,
          extracurricular_activities_count: 10,
        },
        issuer: "did:cheqd:testnet:3d8707e1-2425-4be9-ba41-0ad0c8a06f93",
        issuanceDate: createdDate.toISOString(),
        expirationDate: expiredDate.toISOString(),
      },
      revocable: true,
    });

    const response = await fetch("https://api-testnet.truvera.io/credentials", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${jwt}`,
        "Content-Type": "application/json",
      },
      body,
    }).then((data) => {
      return data.json();
    });
    console.log(response);
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
      name: "Student Loan Verification",
      purpose:
        "Verify a student's eligibility for a loan program based on issued academic credentials.",
      input_descriptors: null,
      expirationTime: {
        amount: 1,
        unit: "months",
      },
      did: process.env.VERIFIER_DID,
    });
    const response = await api.post(`/proof-templates`, body);
    return await response.json();
  } catch (error) {
    console.error("Error creating proof template:", error);
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
// getProofRequestById("2d40ca6e-e26b-45bf-abe3-eff0a4f26789")

const response = await fetch(
  "https://api-testnet.truvera.io/proof-templates",
  {
    method: "GET",
    headers: {
      Authorization: `Bearer ${jwt}`,
      Accept: "*/*",
    },
  }
);

