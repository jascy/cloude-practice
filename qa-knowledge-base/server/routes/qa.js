const express = require('express');
const router = express.Router();
const QAController = require('../controllers/qaController');

// 问答 CRUD
router.get('/qa', QAController.list);
router.get('/qa/:id', QAController.detail);
router.post('/qa', QAController.create);
router.put('/qa/:id', QAController.update);
router.delete('/qa/:id', QAController.delete);

// 搜索
router.get('/search', QAController.search);
router.get('/suggest', QAController.suggest);

// 分类
router.get('/categories', QAController.categories);

module.exports = router;
