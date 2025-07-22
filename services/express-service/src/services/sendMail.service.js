// Tạo tài khoản mới Ethereal để test
import nodemailer from 'nodemailer';

// const testAccount = await nodemailer.createTestAccount(); // 👈 tạo tài khoản tạm

const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
        user: process.env.SMTP_USER, // ví dụ: yourgmail@gmail.com
        pass: process.env.SMTP_PASS, // app password (không phải mật khẩu Gmail)
    },
});


export const sendVerificationEmail = async (to, token) => {
    console.log(process.env.SMTP_USER, process.env.SMTP_PASS);
  const mailOptions = {
    from: process.env.SMTP_USER, // địa chỉ email gửi
    to,
    subject: 'Xác minh tài khoản của bạn',
    html: `
      <p>Nhấn vào link sau để xác minh tài khoản:</p>
      <a href="http://localhost:5173/verify-email?token=${token}">Xác minh</a>
    `,  
  };

  await transporter.sendMail(mailOptions);
};
