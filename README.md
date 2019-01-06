# nand2tetris

## HDLの記述で参考になったもの

- Nand, DFFは予め用意されている
```
Nand(a=a, b=b, out=c0);
DFF(in=input, out=nowout, out=out);
```
- 出力は複数書ける  
出力を別回路の入力としたい場合等に利用
```
DFF(in=input, out=nowout, out=out);
```
- 複数ビットの代入
```
IN a[16], b[16];
OUT out[16];

PARTS:
// 16bitの入出力, a[0]=a[0], a[1]=a[1]... a[15]=a[15]と書く必要はない
And16(a=a, b=b, out=out); 
// 一部ビットを抜きだす記述(スライス表記)
// スライス表記は、自分で定義したピン(IN, OUTに定義されていないピン)では使用できないので注意
Or8Way(in[0..5]=a[0..5], in[6..7]=b[0..1], out=out, out=myout); 
```
- 入力ピンにはtrue, falseを指定可能
```
And16(a=a, b=true, out=out); // 常にb=1
```

**参考にさせて頂いたサイト**

ひとりNand2Tetris  
- http://blog.tojiru.net/article/426525167.html
- http://blog.tojiru.net/article/426464326.html
