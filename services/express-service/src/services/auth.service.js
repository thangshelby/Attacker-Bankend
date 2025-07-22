import nodemailer from "nodemailer";
import twilio from "twilio";

const transporter = nodemailer.createTransport({
  host: "smtp.gmail.com",
  secure: true,
  port: "465",
  auth: {
    user: "n.nducthangg@gmail.com",
    pass: "rjty sbol gdhc twpj",
  },
});

export const sendOtpEmail = async (to, otp) => {
  const mailOptions = {
    from: "n.nducthangg@gmail.com",
    to,
    subject: "Mã OTP xác thực tài khoản",
    html: `
      <div style="font-family: sans-serif;">
        <p>Xin chào,</p>
        <p>Mã OTP của bạn là:</p>
        <h2 style="color: #702272;">${otp}</h2>
        <p>Vui lòng nhập mã này để tiếp tục quá trình xác thực. Mã có hiệu lực trong vòng 5 phút.</p>
        <p>Trân trọng,<br />Đội ngũ hỗ trợ</p>
      </div>
    `,
  };

  try {
    await transporter.sendMail(mailOptions);
    console.log(`OTP email sent to ${to}`);
  } catch (error) {
    console.error("Failed to send OTP email:", error);
    throw error;
  }
};

sendOtpEmail("n.nducthangg@gmail.com", "123");

const client = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

export const sendOtpSms = async (phoneNumber, otp) => {
  try {
    const message = await client.messages.create({
      body: `Mã OTP của bạn là: ${otp}`,
      from: process.env.TWILIO_PHONE_NUMBER, // số điện thoại đã đăng ký trong Twilio
      to: phoneNumber, // ví dụ: "+849xxxxxxxx"
    });

    console.log(`OTP sent to ${phoneNumber}: ${message.sid}`);
    return message.sid;
  } catch (error) {
    console.error("Error sending OTP via SMS:", error);
    throw error;
  }
};
