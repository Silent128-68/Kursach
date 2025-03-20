<template>
  <div id="app">
    <router-link to="/">Home</router-link>

    <!-- Кнопки для перехода между секциями -->
    <button @click="showDetailTypesPage">Виды деталей</button>
    <button @click="showSchemesPage">Схемы</button>
    <button @click="showCheckAssemblyPageMethod">Проверка сборки</button>

    <!-- Список типов деталей -->
    <div v-if="showDetailTypes && detailTypes.length">
      <h3>Виды деталей</h3>
      <ul>
        <li v-for="type in detailTypes" :key="type.id">
          {{ type.name }}: {{ type.quantity }} ({{ type.type }})
          <button @click="deleteDetailType(type.id)">Удалить</button>
          <button @click="openAddModal(type)">Добавить</button>
        </li>
      </ul>
    </div>

    <!-- Список схем -->
    <div v-if="showSchemes && schemes.length">
      <h3>Схемы</h3>
      <!-- Кнопка для создания новой схемы -->
      <button @click="openCreateSchemeModal">Создать новую схему</button>
      <ul>
        <li v-for="scheme in schemes" :key="scheme.id">
          <button @click="fetchDetailsForScheme(scheme.id)">
            {{ scheme.scheme_name }}
          </button>
          <button @click="deleteScheme(scheme.id)">Удалить</button>
        </li>
      </ul>
    </div>

    <!-- Страница для проверки сборки -->
    <div v-if="showCheckAssemblyPage">
      <h3>Проверка сборки</h3>

      <!-- Список доступных схем -->
      <div v-if="schemes.length">
        <h4>Выберите схему для проверки сборки:</h4>
        <ul>
          <li v-for="scheme in schemes" :key="scheme.id">
            <div>
              <button @click="checkAssemblyForScheme(scheme.id)">
                Проверить сборку для {{ scheme.scheme_name }}
              </button>
            </div>
          </li>
        </ul>
      </div>

      <!-- Результат проверки сборки -->
      <div v-if="assemblyCheckResult" class="assembly-check-result">
        <h3>Результат проверки:</h3>
        <p>{{ assemblyCheckResult }}</p>

        <!-- Если сборка невозможна, показываем недостающие детали -->
        <div v-if="missingDetails.length">
          <h4>Недостающие детали:</h4>
          <ul>
            <li v-for="detail in missingDetails" :key="detail.detail_name">
              {{ detail.detail_name }} ({{ detail.type}}): требуется {{ detail.required }}, доступно {{ detail.available }}, не хватает {{ detail.missing }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Список деталей выбранной схемы -->
    <div v-if="showDetailsForScheme">
      <h3>Детали для выбранной схемы</h3>
      <!-- Если деталей нет, показываем кнопку для добавления -->
      <ul v-if="selectedSchemeDetails.length > 0">
        <li v-for="detail in selectedSchemeDetails" :key="detail.id">
          {{ detail.name }}: {{ detail.quantity }} ({{ detail.type }})
        </li>
      </ul>
      <button @click="openAddDetailToSchemeModal">Добавить деталь в схему</button>
    </div>

     <!-- Модальное окно для изменения количества -->
     <div v-if="isAddModalOpen" class="modal">
      <div class="modal-content">
        <h3>Добавить количество к {{ selectedDetailType?.name }}</h3>
        <input type="number" v-model.number="additionalQuantity" placeholder="Введите количество" />
        <button @click="addQuantity">Принять</button>
        <button @click="closeAddModal">Отменить</button>
      </div>
    </div>

    <!-- Модальное окно для добавления новой детали к схеме -->
    <div v-if="isAddDetailToSchemeModalOpen" class="modal">
      <div class="modal-content">
        <h3>Выберите деталь и её количество для добавления в схему</h3>

        <form @submit.prevent="addDetailToScheme">
          <!-- Выпадающий список типов деталей -->
          <select v-model="selectedDetailTypeToAdd" required>
            <option v-for="type in detailTypes" :key="type.id" :value="type">
              {{ type.name }} ({{ type.type}})
            </option>
          </select>

          <!-- Поле для ввода количества -->
          <input type="number" v-model.number="newDetailQuantity" placeholder="Введите количество" required />

          <button @click="addDetailToScheme">Добавить в схему</button>
          <button @click="closeAddDetailToSchemeModal">Отменить</button>
        </form>
      </div>
    </div>

    <!-- Модальное окно для создания новой схемы -->
    <div v-if="isCreateSchemeModalOpen" class="modal">
      <div class="modal-content">
        <h3>Создать новую схему</h3>
        <form @submit.prevent="createScheme">
          <input type="text" v-model="newSchemeName" placeholder="Введите название схемы" required />
          <button type="submit">Создать</button>
          <button @click="closeCreateSchemeModal">Отменить</button>
        </form>
      </div>
    </div>


  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      detailTypes: [],
      schemes: [],
      selectedSchemeDetails: [],
      showDetailTypes: false,
      showSchemes: false,
      showDetailsForScheme: false,
      isAddModalOpen: false,
      isAddDetailToSchemeModalOpen: false,
      addQuantityValue: 0,
      selectedDetailTypeId: null,
      selectedDetailType: null,
      additionalQuantity: 0,
      selectedDetailTypeToAdd: null,
      newDetailQuantity: 0,
      selectedSchemeId: null,
      showSchemeSelection: false,
      assemblyCheckResult: null,
      missingDetails: [],
      showCheckAssemblyPage: false,
      isCreateSchemeModalOpen: false,  // Состояние модального окна для создания схемы
      newSchemeName: '',  // Название новой схемы
    };
  },
  created() {
    // Загрузка доступных типов деталей с сервера
    this.fetchDetailTypes();
  },
  methods: {
      // Показать страницу с типами деталей
    showDetailTypesPage() {
      this.showDetailTypes = true;
      this.showSchemes = false;
      this.showCheckAssemblyPage = false;
      this.showDetailsForScheme = false;
    },

    // Показать страницу со схемами
    async showSchemesPage() {
      this.showDetailTypes = false;
      this.showSchemes = true;
      this.showCheckAssemblyPage = false;
      this.showDetailsForScheme = false;

      await this.fetchSchemes(); // Обязательно вызываем загрузку схем
    },


    // Показать страницу проверки сборки
    async showCheckAssemblyPageMethod() {
      this.showDetailTypes = false;
      this.showSchemes = false;
      this.showCheckAssemblyPage = true;
      this.showDetailsForScheme = false;

    },
    async fetchDetailTypes() {
      try {
        this.showDetailTypes = true;
        this.showSchemes = false;
        this.showDetailsForScheme = false;
        const response = await axios.get('http://localhost:8000/detail_types');
        this.detailTypes = response.data;
      } catch (error) {
        console.error('Error fetching detail types:', error);
      }
    },
    async fetchSchemes() {
      try {
        this.showSchemes = true;
        this.showDetailTypes = false;
        this.showDetailsForScheme = false;
        const response = await axios.get('http://localhost:8000/schemes');
        this.schemes = response.data;
        this.schemeDetails = response.data;
      } catch (error) {
        console.error('Error fetching schemes:', error);
      }
    },
    async fetchDetailsForScheme(schemeId) {
      try {
        this.showDetailsForScheme = true;
        this.showDetailTypes = false;
        this.showSchemes = false;
        this.selectedSchemeId = schemeId;
        const response = await axios.get(`http://localhost:8000/schemes/${schemeId}/details`);
        this.selectedSchemeDetails = response.data; // Присваиваем полученные данные

        // Если в схеме нет деталей, показываем кнопку добавления
        if (this.selectedSchemeDetails.length === 0) {
          this.showAddDetailButton = true;  // Показываем кнопку добавления детали
        } else {
          this.showAddDetailButton = false;  // Если детали есть, кнопка не нужна
        }
      } catch (error) {
        console.error('Error fetching details for scheme:', error);
      }
    },
    async deleteDetailType(id) {
      try {
        await axios.delete(`http://localhost:8000/detail_types/${id}`);
        this.fetchDetailTypes();
      } catch (error) {
        console.error('Error deleting detail type:', error);
      }
    },
    async deleteScheme(id) {
      try {
        await axios.delete(`http://localhost:8000/schemes/${id}`);
        this.fetchSchemes();
      } catch (error) {
        console.error('Error deleting scheme:', error);
      }
    },
    // Метод для удаления детали из схемы
    async remove_detail_from_scheme(detailTypeId) {
      try {
        // Отправка DELETE запроса для удаления детали из схемы
        const response = await axios.delete(`http://localhost:8000/schemes/${this.selectedSchemeId}/remove_detail/${detailTypeId}`);
        
        if (response.status === 200) {
          // Удаляем деталь из локального списка, чтобы обновить интерфейс
          this.selectedSchemeDetails = this.selectedSchemeDetails.filter(detail => detail.detail_type_id !== detailTypeId);
        }
      } catch (error) {
        console.error('Error deleting detail from scheme:', error);
      }
    },
    openAddModal(type) {
      this.selectedDetailType = type;
      this.isAddModalOpen = true;
    },
    closeAddModal() {
      this.isAddModalOpen = false;
      this.selectedDetailType = null;
      this.additionalQuantity = 0;
    },
    // Обработка добавления количества
    async addQuantity() {
      try {
        if (this.additionalQuantity > 0 && this.selectedDetailType) {
          // Отправка PUT запроса на сервер для изменения количества в БД
          const response = await axios.put(`http://localhost:8000/detail_types/${this.selectedDetailType.id}/add`, {
            quantity: this.additionalQuantity
          });

          if (response.status === 200) {
            // Обновление локального списка типов деталей после успешного запроса
            const updatedDetail = response.data; // Данные, которые вернутся с сервера
            const index = this.detailTypes.findIndex(item => item.id === updatedDetail.id);
            if (index !== -1) {
              this.detailTypes[index].quantity = updatedDetail.quantity; // Обновляем количество
            }

            // Закрытие модального окна
            this.closeAddModal();
          } else {
            console.error('Failed to update quantity');
          }
        }
      } catch (error) {
        console.error('Error adding quantity:', error);
      }
    },
    openAddDetailToSchemeModal() {
      this.isAddDetailToSchemeModalOpen = true;
      this.newDetailQuantity = 0;
      this.selectedDetailTypeToAdd = null;
    },
    // Метод для добавления детали в схему
    async addDetailToScheme() {
      try {
        if (this.newDetailQuantity > 0 && this.selectedDetailTypeToAdd) {
          // Отправляем POST запрос на добавление детали в схему
          const response = await axios.post(`http://localhost:8000/schemes/${this.selectedSchemeId}/add_detail`, {
            detail_type_id: this.selectedDetailTypeToAdd.id,
            quantity: this.newDetailQuantity
          });

          if (response.status === 200) {
            this.closeAddDetailToSchemeModal(); // Закрываем модальное окно после добавления

            // Обновляем список деталей схемы
            await this.fetchDetailsForScheme(this.selectedSchemeId);

          }
        }
      } catch (error) {
        console.error("Error adding detail to scheme:", error);
      }
    },
    closeAddDetailToSchemeModal() {
      this.isAddDetailToSchemeModalOpen = false;
      this.newDetailQuantity = 0; // Сбрасываем значение количества
      this.selectedDetailTypeToAdd = null; // Сбрасываем выбранный тип детали
    },
    async checkAssemblyForScheme(schemeId) {
      try {
        // Запоминаем выбранную схему
        this.selectedSchemeId = schemeId;

        // Отправляем запрос на сервер для проверки сборки схемы
        const response = await axios.get(`http://localhost:8000/schemes/${schemeId}/can_assemble`);
        const result = response.data;

        // Проверка успешности сборки и вывод соответствующего результата
        if (result.assembly_possible) {
          this.assemblyCheckResult = `Схема ${result.scheme_name} может быть собрана!`;
          this.missingDetails = [];  // Нет недостающих деталей
        } else {
          this.assemblyCheckResult = `Схема ${result.scheme_name} не может быть собрана.`;
          this.missingDetails = result.missing_details;  // Присваиваем недостающие детали
        }
      } catch (error) {
        console.error('Ошибка при проверке сборки схемы:', error);
        this.assemblyCheckResult = 'Не удалось проверить возможность сборки схемы. Попробуйте позже.';
        this.missingDetails = [];
      }
    },
    // Открытие модального окна для создания новой схемы
    openCreateSchemeModal() {
      this.isCreateSchemeModalOpen = true;
    },

    // Закрытие модального окна
    closeCreateSchemeModal() {
      this.isCreateSchemeModalOpen = false;
      this.newSchemeName = '';  // Сбрасываем название схемы
    },

    // Метод для создания новой схемы
    async createScheme() {
      try {
        if (this.newSchemeName.trim()) {
          const response = await axios.post('http://localhost:8000/schemes', {
            scheme_name: this.newSchemeName,
          });

          // Если схема успешно создана, добавляем её в локальный список схем
          this.schemes.push(response.data);
          this.closeCreateSchemeModal();  // Закрываем модальное окно
        } else {
          alert('Please enter a valid name for the scheme.');
        }
      } catch (error) {
        console.error('Error creating scheme:', error);
        alert('There was an error creating the scheme. Please try again.');
      }
    },
  }
};
</script>

<style>
/* Стиль для модальных окон */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 5px;
  width: 300px;
  max-width: 100%;
}

/* Стиль для кнопок */
button {
  margin: 5px;
  padding: 10px;
  font-size: 14px;
  cursor: pointer;
}

button:hover {
  background-color: #007bff;
  color: white;
}


</style>
