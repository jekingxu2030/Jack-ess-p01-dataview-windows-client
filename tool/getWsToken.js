
// const CryptoJS=require("crypto-js");

// class Be {
//   constructor(key="HbdEmsCloudServe",iv="") {
//     this.SecretPassphrase=key;
//     this.IV=iv;
//     this.key=CryptoJS.enc.Utf8.parse(key);
//     this.iv=CryptoJS.enc.Utf8.parse(iv);
//   }

//   encrypt(data) {
//     if(typeof data==="object") {
//       try {
//         data=JSON.stringify(data);
//       } catch(e) {
//         console.error("Stringify error:",e);
//       }
//     }
//     const srcs=CryptoJS.enc.Utf8.parse(data);
//     return CryptoJS.AES.encrypt(srcs,this.key,{
//       iv: this.iv,
//       mode: CryptoJS.mode.ECB,
//       padding: CryptoJS.pad.Pkcs7
//     }).ciphertext.toString();
//   }
// }

// // 使用示例
// const encryptor=new Be();
// const userId="47";
// const saToken="yCiRYvQLpxtmJAk0WbWgDYFiKwSy2lDeGuzJFpN1xDYwN9Gza3hkwKmMXGEIDq5z";
// const locale="zh-CN";
// const keyless=encryptor.encrypt(`${userId};${saToken};${locale}`);

// console.log(keyless); // 输出512位十六进制字符串


// const CryptoJS=require("crypto-js");

// class Z {
//   constructor(key="HbdEmsCloudServe") {
//     // 关键修正：使用MD5散列密钥
//     this.key=CryptoJS.MD5(key).toString();
//   }

//   static encrypt(data) {
//     const instance=new Z();
//     const key=CryptoJS.enc.Hex.parse(instance.key);
//     const srcs=CryptoJS.enc.Utf8.parse(data);

//     return CryptoJS.AES.encrypt(srcs,key,{
//       mode: CryptoJS.mode.ECB,
//       padding: CryptoJS.pad.Pkcs7,
//       iv: CryptoJS.enc.Hex.parse("") // 显式声明空IV
//     }).toString(); // 原网站可能返回Base64格式
//   }
// }

// // 测试用例
// const encrypted=Z.encrypt("47;yCiRYvQLpxtmJAk0WbWgDYFiKwSy2lDeGuzJFpN1xDYwN9Gza3hkwKmMXGEIDq5z;zh-CN");
// console.log(encrypted);

// const CryptoJS=require("crypto-js");

// function encryptToken(token) {
//   const rawKey="HbdEmsCloudServe";
//   const md5Key=CryptoJS.MD5(rawKey).toString();
//   const key=CryptoJS.enc.Hex.parse(md5Key);
//   const srcs=CryptoJS.enc.Utf8.parse(token);

//   const encrypted=CryptoJS.AES.encrypt(srcs,key,{
//     mode: CryptoJS.mode.ECB,
//     padding: CryptoJS.pad.Pkcs7,
//     iv: "" // 强制空IV
//   });

//   return encrypted.ciphertext.toString(); // 十六进制输出
// }

// // 测试用例
// const token="yCiRYvQLpxtmJAk0WbWgDYFiKwSy2lDeGuzJFpN1xDYwN9Gza3hkwKmMXGEIDq5z";
// console.log(encryptToken(token));



const CryptoJS=require("crypto-js");

function encryptToken(token) {
  // 关键修正步骤
  const rawKey="HbdEmsCloudServe";
  const md5Key=CryptoJS.MD5(rawKey).toString();
  const key=CryptoJS.enc.Hex.parse(md5Key);
  const srcs=CryptoJS.enc.Utf8.parse(token);

  // 强制ECB模式+空IV
  const encrypted=CryptoJS.AES.encrypt(srcs,key,{
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7,
    iv: CryptoJS.enc.Hex.parse("") // 显式声明空IV
  });

  // 转换为目标十六进制格式
  return encrypted.ciphertext.toString();
}

// 验证用例
const target="4a50518c47c81dfb9742d2807968d022..."; // 您的目标结果
const actual=encryptToken("yCiRYvQLpxtmJAk0WbWgDYFiKwSy2lDeGuzJFpN1xDYwN9Gza3hkwKmMXGEIDq5z");
console.log(actual===target.slice(0,actual.length)); // 长度比对
