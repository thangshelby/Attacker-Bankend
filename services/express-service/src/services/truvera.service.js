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
      password,
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
          id: student_DID,
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
    console.log(response.data);
    return await response.json();
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

// export const issueVcc = async ({
//   studentDid,
//   recipientEmail,
//   subject,
//   password = "securepass",
// }) => {
//   const createdDate = new Date();
//   const expiredDate = new Date(createdDate);
//   expiredDate.setMonth(createdDate.getMonth() + 4);
//   const jwt="eyJzY29wZXMiOlsidGVzdCIsImFsbCJdLCJzdWIiOiIxOTQ1MyIsInNlbGVjdGVkVGVhbUlkIjowLCJjcmVhdG9ySWQiOiIxOTQ1MyIsImZtdCI6MSwiaWF0IjoxNzUzMTUyMzg2LCJleHAiOjQ4MzI0NDgzODZ9.Bta9N3ReZywgDH90SRnySvXqDGLat40ecf4yCaYIXpHRUatz0AIuooIPf4wAXJh4z1aDtZxgvTMh4hgJyMWD9g"
//   try {
//     const body = JSON.stringify({
//       persist: true,
//       password,
//       recipientEmail,
//       algorithm: "ed25519", // hoặc "dockbbs" nếu cần ZKP
//       distribute: false, // hoặc false nếu muốn gửi thủ công
//       format: "jsonld",
//       credential: {
//         name: "Student Loan Eligibility Credential",
//         description:
//           "Credential to assess student's eligibility for financial support and loans.",
//         schema:
//           "https://schema.truvera.io/StudentLoanEligibilitySchema-V2-1754100871243.json",
//         context:
//           "https://schema.truvera.io/StudentLoanEligibilitySchema-V1754100871243.json-ld",
//         type: ["VerifiableCredential", "StudentLoanEligibilitySchema"],
//         subject: {
//           id: studentDid,
//           // name: "ngo nguyen duc thang",
//           curent_gpa: 3.7,
//           gpa: 3.7,
//           has_scholarship: true,
//           scholarship_count: 4,
//           failed_course_count: 0,
//           has_leadership_role: false,
//           academic_award_count: 10,
//           total_credits_earned: 10,
//           extracurricular_activity_count: 10,
//         },
//         issuer: "did:cheqd:testnet:3d8707e1-2425-4be9-ba41-0ad0c8a06f93",
//         issuanceDate: createdDate.toISOString(),
//         expirationDate: expiredDate.toISOString(),
//       },
//       revocable: true,
//     });

//     const response = await fetch("https://api-testnet.truvera.io/credentials", {
//       method: "POST",
//       headers: {
//         Authorization: `Bearer ${jwt}`,
//         "Content-Type": "application/json",
//       },
//       body,
//     }).then((data) => {
//       return data.json();
//     });
//     console.log(response);
//   } catch (error) {
//     console.error("Error issuing VC:", error);
//     return null;
//   }
// };

// issueVcc({})
