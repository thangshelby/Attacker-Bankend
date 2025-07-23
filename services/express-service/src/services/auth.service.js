import nodemailer from "nodemailer";
import twilio from "twilio";
import otpGenerator from "otp-generator";
import dotenv from "dotenv";
dotenv.config();

const transporter = nodemailer.createTransport({
  host: "smtp.gmail.com",
  secure: true,
  port: "465",
  auth: {
    user: `${process.env.SMTP_USER}`,
    pass: `${process.env.SMTP_PASSWORD}`,
  },
});

export const sendOtpEmail = async (toEmailAddress) => {
  const otpToken = await otpGenerator.generate(6, { upperCaseAlphabets: false, specialChars: false });
  const mailOptions = {
    from: "n.nducthangg@gmail.com",
    to: toEmailAddress,
    subject: "Mã OTP xác thực tài khoản",
    html: `
      <div style="font-family: sans-serif;">
        <p>Xin chào,</p>
        <p>Mã OTP của bạn là:</p>
        <h2 style="color: #702272;">${otpToken}</h2>
        <p>Vui lòng nhập mã này để tiếp tục quá trình xác thực. Mã có hiệu lực trong vòng 5 phút.</p>
        <p>Trân trọng,<br />Đội ngũ hỗ trợ</p>
      </div>
    `,
  };

  try {
    await transporter.sendMail(mailOptions);
    return otpToken; // Trả về mã OTP để lưu trữ hoặc sử dụng sau này
  } catch (error) {
    console.error("Failed to send OTP email:", error);
    throw error;
  }
};

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
