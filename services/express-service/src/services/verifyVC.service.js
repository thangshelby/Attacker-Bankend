import { Resolver } from "did-resolver";
import { getResolver } from "key-did-resolver";

export async function verifyVC(jwt) {
  // Khởi tạo DID resolver cho did:key
  const resolver = new Resolver(getResolver());

  try {
    const verifiedVC = await verifyCredential(jwt, resolver);
    console.log("✅ VC hợp lệ!");
    console.log("Payload:", verifiedVC.verifiableCredential);
    return verifiedVC;
  } catch (error) {
    console.error("❌ VC không hợp lệ!");
    console.error(error);
    return null;
  }
}
