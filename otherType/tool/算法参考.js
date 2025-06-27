var N=Object.defineProperty;
var v=(s,e,t) => e in s? N(s,e,{
  enumerable: !0,
  configurable: !0,
  writable: !0,
  value: t
}):s[e]=t;
var c=(s,e,t) => v(s,typeof e!="symbol"? e+"":e,t);
import { c2 as y,by as A,b$ as O,c0 as I,a0 as W,k as C,aS as P,U as h,X as R,aV as D,i as m,$ as p } from "./index-ChrGRWLt.js";
import { b as E } from "./_baseUniq-BSpWKAIX.js";
import { i as L } from "./_arrayIncludesWith-CcGSYvBB.js";
import { A as $,f as b } from "./index-C3uPhpgc.js";
import { c as S,s as T,g as k } from "./index-DZ7qh3EL.js";
var _=Object.prototype
  ,x=_.hasOwnProperty;
function M(s,e) {
  return s!=null&&x.call(s,e)
}
function U(s,e) {
  return s!=null&&y(s,e,M)
}
function w(s,e,t,n) {
  return n=typeof n=="function"? n:void 0,
    s==null? s:A(s,e,t,n)
}
function F(s,e) {
  return e=typeof e=="function"? e:void 0,
    s&&s.length? E(s,void 0,e):[]
}
const J=I({
  id: "noticeList",
  state: () => ({
    noticeObj: {}
  }),
  actions: {
    save(s,e,t,n) {
      const o=`${s}.${e}.${t}`;
      let i={
        ...this.noticeObj
      };
      if(U(i,o)) {
        let r=W(i,o);
        r=F([...n,...r],L),
          w(i,o,r,Object)
      } else
        w(i,o,n,Object);
      this.noticeObj={
        ...i
      }
    }
  }
});
function X() {
  return J(O)
}
const u=C()
  ,q=X()
  ,G=new D
  ,Z=new $;
let B=`ws://${window.location.hostname}:8888`
  ,g=15*1e3;
class H {
  constructor(e,t) {
    c(this,"emsId");
    c(this,"keyless");
    c(this,"p",Promise.resolve());
    c(this,"socket");
    c(this,"onceFunArr",m([]));
    c(this,"wsData",m({
      menu: {},
      rtv: [],
      log: [],
      cfg: 0,
      expire: {},
      log_data: [],
      ctl: [],
      policy: {}
    }));
    c(this,"timer",null);
    c(this,"MRDA",{});
    c(this,"shouldReconnect",!0);
    c(this,"keep",() => {
      clearInterval(this.timer),
        this.timer=setInterval(() => {
          let e=new Uint8Array([9]);
          this.socket.send(e)
        }
          ,30*1e3)
    }
    );
    c(this,"onmessage",e => {
      let t=e.data;
      if(!(t instanceof Blob)) {
        if(t=JSON.parse(t),
          b(this.onceFunArr,(n,o) => {
            n(t)&&this.onceFunArr.slice(o,o+1)
          }
          ),
          t.func==="rtv"&&(t.data=t.data.map(n => ({
            ...n,
            value: S(n.value,2)
          }))),
          t.func==="log_data") {
          this.wsData[t.func]=[...t.data,...this.wsData[t.func]];
          return
        }
        t.func==="expire"&&(t.data={
          ...t.data,
          his_data: T(t.data.his_data).map(n => {
            const o=Object.keys(n).find(i => !isNaN(Number(i)))||"";
            return {
              ...n,
              [o]: S(n[o],2)
            }
          }
          )
        }),
          this.wsData[t.func]=t.data,
          t.func==="log"&&this.wsData.log.length&&q.save(this.emsId,p().startOf("date").valueOf(),p().endOf("date").valueOf(),t.data),
          t.func==="refresh"&&this.onRefresh(),
          t.func==="timezone"&&localStorage.setItem("timezone",t.data)
      }
    }
    );
    c(this,"onRefresh",() => {
      window.sessionStorage.setItem("autoRefresh",this.emsId),
        location.reload()
    }
    );
    c(this,"close",() => {
      this.shouldReconnect=!1,
        this.socket.close()
    }
    );
    c(this,"onclose",() => {
      clearInterval(this.timer),
        this.shouldReconnect&&setTimeout(() => {
          this.connect(),
            this.p.then(() => {
              h(this.MRDA,(e,t) => {
                this.send(e)
              }
              )
            }
            )
        }
          ,g)
    }
    );
    c(this,"onerror",e => {
      setTimeout(() => {
        this.connect()
      }
        ,g)
    }
    );
    this.emsId=e,
      this.keyless=t,
      this.connect()
  }
  connect() {
    this.p=new Promise((e,t) => {
      let o=0;
      const i=() => {
        const a=new WebSocket(`${B}/${this.emsId}?${this.keyless}`);
        this.socket=a,
          a.onopen=this.onopen(e),
          a.onmessage=this.onmessage,
          a.onclose=this.onclose,
          this.keep();
        const r=3*1e3;
        setTimeout(() => {
          a.readyState===WebSocket.CONNECTING&&(console.warn("WebSocket 一直处于 CONNECTING 状态，可能已挂起，尝试重连"),
            a.close(),
            this.shouldReconnect=!1,
            o++,
            o<3? i():t())
        }
          ,r)
      }
        ;
      i()
    }
    )
  }
  onopen(e) {
    return () => {
      this.shouldReconnect=!0,
        this.socket.onerror=this.onerror,
        e()
    }
  }
  send(e) {
    return new Promise((t,n) => {
      const o=this.socket
        ,i={
          ...e
        }
        ,a=i.funcAck||i.func;
      delete i.funcAck,
        o.readyState===WebSocket.OPEN? (this.MRDA[i.func]=i,
          o.send(JSON.stringify(i)),
          this.onceFunArr.unshift(r => {
            var f;
            let d=r.func
              ,l=a;
            return i.id&&((f=r==null? void 0:r.data)!=null&&f.id)&&(d+=r.data.id,
              l+=i.id),
              d===l&&t(r),
              d===l
          }
          )):(n(),
            console.error("无法发送消息，因为连接未打开或正在关闭"))
    }
    )
  }
  sendtimeZone() {
    return V.call(this)
  }
  sendMenu() {
    return this.send({
      func: "menu"
    })
  }
  sendRtv(e) {
    return this.send({
      func: "rtv",
      period: 0,
      ids: e
    })
  }
  sendExpire(e) {
    let t=JSON.stringify((e==null? void 0:e.ids)||[]);
    return this.send({
      func: "expire",
      ...e,
      begin: Number(e.begin)+k(),
      end: Number(e.end)+k(),
      ids: t
    })
  }
  sendExport(e) {
    let t=JSON.stringify((e==null? void 0:e.ids)||[]);
    return this.send({
      func: "export",
      ...e,
      ids: t
    })
  }
  sendLog(e) {
    return this.send({
      func: "log",
      ...e
    })
  }
  sendCfg(e) {
    return this.send({
      func: "cfg",
      ...e
    })
  }
  clearRtv() {
    this.wsData.rtv=[]
  }
  sendCtl() {
    return this.send({
      func: "ctl"
    })
  }
  sendCmd(e) {
    return this.send({
      func: "cmd",
      funcAck: "cmd_ack",
      ...e
    })
  }
  sendPolicy(e) {
    return this.send({
      func: "policy",
      ...e
    })
  }
}
const K=I({
  id: "ws",
  state: () => ({
    emsIdList: {},
    socket: {},
    menuP: {},
    keyless: ""
  }),
  getters: {},
  actions: {
    connectionWS() {
      var s,e;
      (e=(s=u.powerStation)==null? void 0:s[0])!=null&&e.userId&&(this.keyless=Z.encrypt(`${u.powerStation[0].userId};${G.get("sa-token")};${localStorage.getItem("locale")}`),
        h(u.powerStation,t => {
          this.setEmsId(t.emsId)
        }
        ))
    },
    updateConnectionWS() {
      const s=u.powerStation;
      h(this.emsIdList,(e,t) => {
        R(s,{
          emsId: t
        })||(this.socket[t].close(),
          delete this.emsIdList[t],
          delete this.socket[t],
          delete this.menuP[t])
      }
      ),
        this.connectionWS()
    },
    setEmsId(s) {
      if(this.emsIdList[s])
        return this.menuP[s];
      this.emsIdList[s]=!0,
        this.menuP[s]=this.initWS(s).p.then(() => (this.socket[s].sendtimeZone(),
          this.socket[s].send({
            func: "menu"
          })))
    },
    initWS(s) {
      const e=new H(s,this.keyless);
      return this.socket[s]=e,
        e
    },
    clearConnectionWS() {
      h(this.emsIdList,(s,e) => {
        this.socket[e].close(),
          delete this.emsIdList[e],
          delete this.socket[e],
          delete this.menuP[e]
      }
      )
    }
  }
})
  ,V=P(function() {
    this.send({
      func: "timezone"
    })
  });
function se() {
  return K(O)
}
export { X as a,F as b,U as h,se as u };
