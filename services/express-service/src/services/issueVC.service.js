import { createVerifiableCredentialJwt, verifyCredential } from "did-jwt-vc";
import { EdDSASigner } from "did-jwt";
import bs58 from "bs58";
import nacl from "tweetnacl";

function generateDidKey() {
  const keyPair = nacl.sign.keyPair();
  const publicKeyBytes = Buffer.from(keyPair.publicKey);
  const privateKeyBytes = Buffer.from(keyPair.secretKey.slice(0, 64));

  const multicodecPubKey = Buffer.concat([
    Buffer.from([0xed, 0x01]),
    publicKeyBytes,
  ]);
  const did = `did:key:z${bs58.encode(multicodecPubKey)}`;

  return {
    did,
    signer: EdDSASigner(privateKeyBytes),
    keyPair,
    publicKeyBase58: bs58.encode(publicKeyBytes),
  };
}

export async function issueVC() {
  const issuer = generateDidKey();

  const subjectDid = "did:key:UEL_k224141694";

  const credentialPayload = {
    sub: subjectDid,
    nbf: Math.floor(Date.now() / 1000),
    vc: {
      "@context": ["https://www.w3.org/2018/credentials/v1"],
      type: ["VerifiableCredential", "TranscriptCredential"],
      credentialSubject: {
        id: subjectDid,
        fullName: "Nguyễn Văn A",
        studentId: "SV123456",
        gpa: 3.5,
        major: "Công nghệ thông tin",
        graduationYear: 2025,
      },
    },
  };

  // Khởi tạo DID resolver
  const resolver = new Resolver(getResolver());
  console.log(issuer.did, issuer.signer);
  // Tạo VC có chữ ký số từ issuer
  const jwt = await createVerifiableCredentialJwt(credentialPayload, {
    did: issuer.did,
    signer: issuer.signer,
    alg: "EdDSA",
  });

  console.log("✅ VC đã được tạo thành công:");
  console.log(jwt);
}
