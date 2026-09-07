/**
 * shared-data.js — 图书借阅系统原型统一数据层
 * 所有页面共用：图书列表、分类列表、借阅记录、收藏列表均存 localStorage
 * 约定：任何增删改先写 localStorage，再刷新页面 DOM
 */
const LB = (function () {
  const KEY = { books: 'lb_books', cats: 'lb_cats', records: 'lb_records', favs: 'lib_favs', users: 'lib_users', session: 'lib_current_user' };
  const CURRENT_READER = '张三';       // 原型当前登录读者
  const LOAN_DAYS = 30;                // 借期 30 天（可配置参数）

  /* ---------- 基础读写 ---------- */
  function get(key, def) {
    try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : def; }
    catch (e) { return def; }
  }
  function set(key, val) { localStorage.setItem(key, JSON.stringify(val)); }

  /* ---------- 时间工具 ---------- */
  function pad(n) { return n < 10 ? '0' + n : '' + n; }
  function fmt(d) {
    d = d instanceof Date ? d : new Date(d);
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) +
      ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  }
  function daysAgo(n) { const d = new Date(); d.setDate(d.getDate() - n); return d; }
  function daysAfter(d, n) { const x = new Date(d); x.setDate(x.getDate() + n); return x; }

  /* ---------- 种子数据 ---------- */
  function seedCategories() {
    return [
      { id: 1, name: '文学', createdAt: '2024-01-15' },
      { id: 2, name: '科技', createdAt: '2024-01-15' },
      { id: 3, name: '历史', createdAt: '2024-01-20' },
      { id: 4, name: '计算机', createdAt: '2024-02-01' },
      { id: 5, name: '艺术', createdAt: '2024-02-10' }
    ];
  }
  function seedBooks() {
    // categoryId 对应分类表 id
    const raw = [
      { isbn: '9787020002207', title: '红楼梦', author: '曹雪芹', categoryId: 1, publisher: '人民文学出版社', year: '1996', total: 5, color: '#c0392b', summary: '中国古典四大名著之一，以贾、史、王、薛四大家族兴衰为背景，描写贾宝玉与林黛玉、薛宝钗的爱情婚姻悲剧。' },
      { isbn: '9787506365437', title: '活着', author: '余华', categoryId: 1, publisher: '作家出版社', year: '2012', total: 5, color: '#e67e22', summary: '讲述农村人福贵悲惨的人生遭遇，亲人相继离他而去，唯有一头老牛陪伴终老，展现生命的坚韧与活着的本义。' },
      { isbn: '9787544253994', title: '百年孤独', author: '加西亚·马尔克斯', categoryId: 1, publisher: '南海出版公司', year: '2011', total: 3, color: '#8e44ad', summary: '魔幻现实主义文学代表作，描写布恩迪亚家族七代人的传奇故事与马孔多小镇的百年兴衰。' },
      { isbn: '9787020008827', title: '西游记', author: '吴承恩', categoryId: 1, publisher: '人民文学出版社', year: '2010', total: 4, color: '#d35400', summary: '中国古典四大名著之一，讲述唐僧师徒四人西天取经、历经九九八十一难的故事。' },
      { isbn: '9787020008834', title: '三国演义', author: '罗贯中', categoryId: 1, publisher: '人民文学出版社', year: '2010', total: 4, color: '#b03a2e', summary: '中国古典四大名著之一，描写东汉末年至西晋初年魏、蜀、吴三国的政治军事斗争。' },
      { isbn: '9787506376600', title: '苏菲的世界', author: '乔斯坦·贾德', categoryId: 1, publisher: '作家出版社', year: '2017', total: 3, color: '#2980b9', summary: '一部以小说形式写成的西方哲学史，少女苏菲在神秘导师引导下踏上哲学探索之旅。' },
      { isbn: '9787536692930', title: '三体', author: '刘慈欣', categoryId: 2, publisher: '重庆出版社', year: '2008', total: 5, color: '#16a085', summary: '亚洲首部雨果奖获奖科幻作品，讲述地球文明与三体文明在宇宙中的生死博弈，是中国科幻里程碑之作。' },
      { isbn: '9787111407010', title: '算法导论', author: 'Thomas H.Cormen', categoryId: 4, publisher: '机械工业出版社', year: '2013', total: 3, color: '#2c3e50', summary: '计算机算法领域的经典教材，全面深入地讨论算法分析与设计，内容严谨、示例丰富。' },
      { isbn: '9787115215700', title: '代码整洁之道', author: 'Robert C.Martin', categoryId: 4, publisher: '人民邮电出版社', year: '2010', total: 3, color: '#27ae60', summary: '软件开发大师 Martin 的经典之作，讲述如何编写可读性强、可维护的整洁代码。' },
      { isbn: '9787549558640', title: '艺术的故事', author: '贡布里希', categoryId: 5, publisher: '广西美术出版社', year: '2014', total: 4, color: '#d4ac0d', summary: '艺术史入门经典，以通俗优美的文字概括从史前洞穴壁画到现代艺术的发展历程。' },
      { isbn: '9787101003040', title: '史记', author: '司马迁', categoryId: 3, publisher: '中华书局', year: '1982', total: 4, color: '#7d6608', summary: '中国第一部纪传体通史，记载了从上古黄帝到汉武帝太初年间约三千年的历史。' },
      { isbn: '9787508647357', title: '人类简史', author: '尤瓦尔·赫拉利', categoryId: 3, publisher: '中信出版社', year: '2014', total: 6, color: '#117a65', summary: '从认知革命、农业革命到科学革命，以宏大视角讲述智人如何成为地球的主宰。' }
    ];
    return raw.map(function (b) {
      return {
        isbn: b.isbn, title: b.title, author: b.author, categoryId: b.categoryId,
        publisher: b.publisher, year: b.year, totalCount: b.total,
        availableCount: b.total, color: b.color, summary: b.summary
      };
    });
  }
  function seedRecords(books) {
    // 借出时间相对“今天”生成，保证演示时逾期/在借状态正确
    function rec(isbn, reader, borrowDaysAgo, returnedDaysAgo) {
      const book = books.filter(function (b) { return b.isbn === isbn; })[0];
      const bt = daysAgo(borrowDaysAgo);
      const r = {
        id: 'R' + Date.now() + Math.floor(Math.random() * 1000) + borrowDaysAgo,
        readerName: reader, username: reader === CURRENT_READER ? 'zhangsan' : 'lisi',
        bookIsbn: isbn, bookTitle: book ? book.title : isbn,
        borrowTime: fmt(bt), dueTime: fmt(daysAfter(bt, LOAN_DAYS)),
        returnTime: '', status: 'borrowed'
      };
      if (returnedDaysAgo != null) {
        r.returnTime = fmt(daysAgo(returnedDaysAgo));
        r.status = 'returned';
      }
      return r;
    }
    const list = [
      rec('9787020002207', CURRENT_READER, 10, null),   // 红楼梦 借阅中
      rec('9787506365437', CURRENT_READER, 5, null),    // 活着 借阅中
      rec('9787101003040', CURRENT_READER, 45, null),   // 史记 逾期
      rec('9787536692930', CURRENT_READER, 40, 35),     // 三体 已归还
      rec('9787544253994', CURRENT_READER, 60, 50),     // 百年孤独 已归还
      rec('9787111407010', CURRENT_READER, 20, 15),     // 算法导论 已归还
      rec('9787020008827', '李四', 8, null),            // 其他读者在借
      rec('9787549558640', '李四', 50, 42)              // 其他读者已归还
    ];
    // 可借数量 = 总馆藏 - 在借（未归还）数量
    books.forEach(function (b) {
      const active = list.filter(function (r) {
        return r.bookIsbn === b.isbn && r.status === 'borrowed';
      }).length;
      b.availableCount = Math.max(0, b.totalCount - active);
    });
    return list;
  }

  /** 首次访问播种；已存在数据则补齐缺失键 */
  function ensureSeed() {
    let books = get(KEY.books, null);
    let cats = get(KEY.cats, null);
    if (!cats) { cats = seedCategories(); set(KEY.cats, cats); }
    if (!books) {
      books = seedBooks();
      const records = seedRecords(books); // 内部会根据在借数调整可借数量
      set(KEY.books, books);
      set(KEY.records, records);
    }
    if (!get(KEY.records, null)) set(KEY.records, []);
    if (!get(KEY.favs, null)) set(KEY.favs, []);
  }

  /* ---------- 分类 ---------- */
  function getCats() { ensureSeed(); return get(KEY.cats, []); }
  function saveCats(list) { set(KEY.cats, list); }
  function catName(id) {
    const c = getCats().filter(function (x) { return x.id === id; })[0];
    return c ? c.name : '未分类';
  }
  function catBookCount(id) {
    return getBooks().filter(function (b) { return b.categoryId === id; }).length;
  }
  function addCat(name) {
    const cats = getCats();
    const id = cats.length ? Math.max.apply(null, cats.map(function (c) { return c.id; })) + 1 : 1;
    const d = new Date();
    cats.push({ id: id, name: name, createdAt: d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) });
    saveCats(cats);
    return id;
  }
  function renameCat(id, name) {
    const cats = getCats();
    cats.forEach(function (c) { if (c.id === id) c.name = name; });
    saveCats(cats);
  }
  /** 删除分类：分类下有图书时返回 false 拦截 */
  function deleteCat(id) {
    if (catBookCount(id) > 0) return false;
    saveCats(getCats().filter(function (c) { return c.id !== id; }));
    return true;
  }

  /* ---------- 图书 ---------- */
  function getBooks() { ensureSeed(); return get(KEY.books, []); }
  function saveBooks(list) { set(KEY.books, list); }
  function getBook(isbn) {
    return getBooks().filter(function (b) { return b.isbn === isbn; })[0] || null;
  }
  function addBook(book) {
    const books = getBooks();
    books.push({
      isbn: book.isbn, title: book.title, author: book.author,
      categoryId: Number(book.categoryId), publisher: book.publisher || '',
      year: book.year || '', totalCount: Number(book.totalCount),
      availableCount: Number(book.totalCount),
      color: book.color || '#34495e', summary: book.summary || '',
      cover_url: book.cover_url || ''
    });
    saveBooks(books);
  }
  function updateBook(isbn, fields) {
    const books = getBooks();
    books.forEach(function (b) {
      if (b.isbn !== isbn) return;
      const oldTotal = b.totalCount;
      if (fields.title != null) b.title = fields.title;
      if (fields.author != null) b.author = fields.author;
      if (fields.categoryId != null) b.categoryId = Number(fields.categoryId);
      if (fields.publisher != null) b.publisher = fields.publisher;
      if (fields.year != null) b.year = fields.year;
      if (fields.summary != null) b.summary = fields.summary;
      if (fields.cover_url != null) b.cover_url = fields.cover_url;
      if (fields.totalCount != null) {
        const newTotal = Number(fields.totalCount);
        // 总馆藏增加时可借数量同步增加；减少时不低于 0
        b.availableCount = Math.max(0, b.availableCount + (newTotal - oldTotal));
        b.totalCount = newTotal;
      }
    });
    saveBooks(books);
  }
  /** 删除图书：图书移除；收藏记录移除；历史借阅记录保留（书名已快照） */
  function deleteBook(isbn) {
    saveBooks(getBooks().filter(function (b) { return b.isbn !== isbn; }));
    saveFavs(getFavs().filter(function (f) { return f.isbn !== isbn; }));
  }

  /* ---------- 借阅 ---------- */
  function getRecords() { ensureSeed(); return get(KEY.records, []); }
  function saveRecords(list) { set(KEY.records, list); }
  /** 获取当前登录会话用户名 */
  function currentUsername() {
    const s = getSession();
    return s ? s.username : '';
  }
  /** 该读者对此书是否有未归还记录（按当前登录用户名匹配） */
  function isBorrowed(isbn) {
    const uname = currentUsername();
    return getRecords().some(function (r) {
      return r.bookIsbn === isbn && r.username === uname && r.status === 'borrowed';
    });
  }
  /** 借阅：校验通过返回 true，生成记录（关联当前登录用户名+姓名）并可借数 -1 */
  function borrow(isbn) {
    const s = getSession();
    if (!s) return { ok: false, msg: '请先登录' };
    const books = getBooks();
    const book = books.filter(function (b) { return b.isbn === isbn; })[0];
    if (!book) return { ok: false, msg: '图书不存在' };
    if (isBorrowed(isbn)) return { ok: false, msg: '您已借阅此书，归还前不可重复借阅' };
    if (book.availableCount <= 0) return { ok: false, msg: '该书已借完' };
    book.availableCount -= 1;
    saveBooks(books);
    const now = new Date();
    const records = getRecords();
    records.unshift({
      id: 'R' + Date.now(),
      username: s.username, readerName: s.realName || s.username,
      bookIsbn: isbn, bookTitle: book.title,
      borrowTime: fmt(now), dueTime: fmt(daysAfter(now, LOAN_DAYS)),
      returnTime: '', status: 'borrowed'
    });
    saveRecords(records);
    return { ok: true };
  }
  /** 当前登录用户的借阅记录 */
  function myRecords() {
    const uname = currentUsername();
    return getRecords().filter(function (r) { return r.username === uname; });
  }
  /** 办理归还：状态变更、填归还时间、可借数 +1 */
  function returnBook(recordId) {
    const records = getRecords();
    let rec = null;
    records.forEach(function (r) { if (r.id === recordId) rec = r; });
    if (!rec || rec.status === 'returned') return false;
    rec.status = 'returned';
    rec.returnTime = fmt(new Date());
    saveRecords(records);
    const books = getBooks();
    books.forEach(function (b) {
      if (b.isbn === rec.bookIsbn && b.availableCount < b.totalCount) b.availableCount += 1;
    });
    saveBooks(books);
    return true;
  }
  /** 派生状态：borrowed 且过了应还时间 → overdue */
  function displayStatus(r) {
    if (r.status === 'returned') return 'returned';
    return new Date(r.dueTime.replace(/-/g, '/')) < new Date() ? 'overdue' : 'borrowed';
  }

  /* ---------- 用户与登录态 ---------- */
  const PRESET_ADMIN = { username: 'admin', password: '123456', role: 'admin', realName: '管理员' };
  /** 用户列表：首次访问播种预置管理员；注册用户追加存入 */
  function getUsers() {
    let users = get(KEY.users, null);
    if (!users) {
      users = [Object.assign({ createdAt: fmt(new Date()) }, PRESET_ADMIN)];
      set(KEY.users, users);
    }
    return users;
  }
  /** 按用户名查找（预置管理员已随播种进入列表） */
  function findUser(username) {
    username = (username || '').trim();
    return getUsers().filter(function (u) { return u.username === username; })[0] || null;
  }
  function usernameExists(username) { return !!findUser(username); }
  function addUser(user) { const users = getUsers(); users.push(user); set(KEY.users, users); }
  /** 修改密码：更新列表中对应用户；预置管理员不在列表时补入 */
  function updateUserPwd(username, newPwd) {
    const users = getUsers();
    let found = false;
    users.forEach(function (u) { if (u.username === username) { u.password = newPwd; found = true; } });
    if (!found && username === PRESET_ADMIN.username) {
      users.push(Object.assign({ createdAt: fmt(new Date()) }, PRESET_ADMIN, { password: newPwd }));
      found = true;
    }
    set(KEY.users, users);
    return found;
  }
  /* 登录态：lib_current_user 存 { username, role, realName } */
  function getSession() { return get(KEY.session, null); }
  function setSession(u) { set(KEY.session, { username: u.username, role: u.role, realName: u.realName }); }
  function clearSession() {
    try { localStorage.removeItem(KEY.session); } catch (e) {}
    try { localStorage.removeItem('lib_token'); } catch (e) {}
  }
  /** 登录拦截：未登录跳转登录页；返回当前用户或 null */
  function requireLogin() {
    const u = getSession();
    if (!u) { location.replace('login.html'); return null; }
    return u;
  }
  /** 角色拦截：未登录跳转登录页；角色不匹配提示"无权限访问"并跳转读者首页 */
  function requireRole(role) {
    const u = getSession();
    if (!u) { location.replace('login.html'); return null; }
    if (u.role !== role) {
      alert('无权限访问');
      location.replace('reader-books.html');
      return null;
    }
    return u;
  }
  /** 更新用户资料（手机号、邮箱），同步写回用户列表 */
  function updateUserProfile(username, profile) {
    const users = getUsers();
    users.forEach(function (u) {
      if (u.username === username) {
        if (profile.phone !== undefined) u.phone = profile.phone;
        if (profile.email !== undefined) u.email = profile.email;
      }
    });
    set(KEY.users, users);
  }
  /** 顶栏渲染当前登录用户：头像（姓名首字，按角色配色）+ 角色（姓名） */
  function renderHeaderUser(avatarId, textId) {
    const u = getSession();
    if (!u) return;
    const av = document.getElementById(avatarId);
    const tx = document.getElementById(textId);
    const name = u.realName || u.username;
    if (av) { av.textContent = name.charAt(0); av.style.background = u.role === 'admin' ? '#409eff' : '#67c23a'; }
    if (tx) tx.textContent = (u.role === 'admin' ? '管理员' : '读者') + '（' + name + '）';
  }

  /* ---------- 收藏 ---------- */
  function getFavs() { ensureSeed(); return get(KEY.favs, []); }
  function saveFavs(list) { set(KEY.favs, list); }
  function isFav(isbn) { return getFavs().some(function (f) { return f.isbn === isbn; }); }
  function toggleFav(isbn) {
    const favs = getFavs();
    const idx = favs.findIndex ? favs.findIndex(function (f) { return f.isbn === isbn; }) : -1;
    if (idx >= 0) {
      favs.splice(idx, 1);
      saveFavs(favs);
      return false;
    }
    const d = new Date();
    favs.push({ isbn: isbn, favTime: d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()) });
    saveFavs(favs);
    return true;
  }

  return {
    KEY: KEY, CURRENT_READER: CURRENT_READER, LOAN_DAYS: LOAN_DAYS,
    fmt: fmt, ensureSeed: ensureSeed,
    getCats: getCats, catName: catName, catBookCount: catBookCount,
    addCat: addCat, renameCat: renameCat, deleteCat: deleteCat,
    getBooks: getBooks, getBook: getBook, addBook: addBook,
    updateBook: updateBook, deleteBook: deleteBook,
    getRecords: getRecords, isBorrowed: isBorrowed, myRecords: myRecords,
    borrow: borrow, returnBook: returnBook, displayStatus: displayStatus,
    getFavs: getFavs, isFav: isFav, toggleFav: toggleFav,
    getUsers: getUsers, findUser: findUser, usernameExists: usernameExists,
    addUser: addUser, updateUserPwd: updateUserPwd, updateUserProfile: updateUserProfile,
    getSession: getSession, setSession: setSession, clearSession: clearSession,
    requireLogin: requireLogin, requireRole: requireRole, renderHeaderUser: renderHeaderUser
  };
})();
